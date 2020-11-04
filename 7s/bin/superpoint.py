import numpy as np
import cv2
import math
import os
import argparse
import torch

# Stub to warn about opencv version.
if int(cv2.__version__[0]) < 3: # pragma: no cover
    print('Warning: OpenCV 3 is not installed')

# Jet colormap for visualization.
myjet = np.array([[0.        , 0.        , 0.5       ],
                  [0.        , 0.        , 0.99910873],
                  [0.        , 0.37843137, 1.        ],
                  [0.        , 0.83333333, 1.        ],
                  [0.30044276, 1.        , 0.66729918],
                  [0.66729918, 1.        , 0.30044276],
                  [1.        , 0.90123457, 0.        ],
                  [1.        , 0.48002905, 0.        ],
                  [0.99910873, 0.07334786, 0.        ],
                  [0.5       , 0.        , 0.        ]])

class SuperPointNet(torch.nn.Module):
  """ Pytorch definition of SuperPoint Network. """
  def __init__(self):
    super(SuperPointNet, self).__init__()
    self.relu = torch.nn.ReLU(inplace=True)
    self.pool = torch.nn.MaxPool2d(kernel_size=2, stride=2)
    c1, c2, c3, c4, c5, d1 = 64, 64, 128, 128, 256, 256
    # Shared Encoder.
    self.conv1a = torch.nn.Conv2d(1, c1, kernel_size=3, stride=1, padding=1)
    self.conv1b = torch.nn.Conv2d(c1, c1, kernel_size=3, stride=1, padding=1)
    self.conv2a = torch.nn.Conv2d(c1, c2, kernel_size=3, stride=1, padding=1)
    self.conv2b = torch.nn.Conv2d(c2, c2, kernel_size=3, stride=1, padding=1)
    self.conv3a = torch.nn.Conv2d(c2, c3, kernel_size=3, stride=1, padding=1)
    self.conv3b = torch.nn.Conv2d(c3, c3, kernel_size=3, stride=1, padding=1)
    self.conv4a = torch.nn.Conv2d(c3, c4, kernel_size=3, stride=1, padding=1)
    self.conv4b = torch.nn.Conv2d(c4, c4, kernel_size=3, stride=1, padding=1)
    # Detector Head.
    self.convPa = torch.nn.Conv2d(c4, c5, kernel_size=3, stride=1, padding=1)
    self.convPb = torch.nn.Conv2d(c5, 65, kernel_size=1, stride=1, padding=0)
    # Descriptor Head.
    self.convDa = torch.nn.Conv2d(c4, c5, kernel_size=3, stride=1, padding=1)
    self.convDb = torch.nn.Conv2d(c5, d1, kernel_size=1, stride=1, padding=0)

  def forward(self, x):
    """ Forward pass that jointly computes unprocessed point and descriptor
    tensors.
    Input
      x: Image pytorch tensor shaped N x 1 x H x W.
    Output
      semi: Output point pytorch tensor shaped N x 65 x H/8 x W/8.
      desc: Output descriptor pytorch tensor shaped N x 256 x H/8 x W/8.
    """
    # Shared Encoder.
    x = self.relu(self.conv1a(x))
    x = self.relu(self.conv1b(x))
    x = self.pool(x)
    x = self.relu(self.conv2a(x))
    x = self.relu(self.conv2b(x))
    x = self.pool(x)
    x = self.relu(self.conv3a(x))
    x = self.relu(self.conv3b(x))
    x = self.pool(x)
    x = self.relu(self.conv4a(x))
    x = self.relu(self.conv4b(x))
    # Detector Head.
    cPa = self.relu(self.convPa(x))
    semi = self.convPb(cPa)
    # Descriptor Head.
    cDa = self.relu(self.convDa(x))
    desc = self.convDb(cDa)
    dn = torch.norm(desc, p=2, dim=1) # Compute the norm.
    desc = desc.div(torch.unsqueeze(dn, 1)) # Divide by norm to normalize.
    return semi, desc


class SuperPointFrontend(object):
  """ Wrapper around pytorch net to help with pre and post image processing. """
  def __init__(self, weights_path, nms_dist, conf_thresh, nn_thresh,
               cuda=False):
    self.name = 'SuperPoint'
    self.cuda = cuda
    self.nms_dist = nms_dist
    self.conf_thresh = conf_thresh
    self.nn_thresh = nn_thresh # L2 descriptor distance for good match.
    self.cell = 8 # Size of each output cell. Keep this fixed.
    self.border_remove = 4 # Remove points this close to the border.

    # Load the network in inference mode.
    self.net = SuperPointNet()
    if cuda:
      # Train on GPU, deploy on GPU.
      self.net.load_state_dict(torch.load(weights_path))
      self.net = self.net.cuda()
    else:
      # Train on GPU, deploy on CPU.
      self.net.load_state_dict(torch.load(weights_path,
                               map_location=lambda storage, loc: storage))
    self.net.eval()

  def nms_fast(self, in_corners, H, W, dist_thresh):
    """
    Run a faster approximate Non-Max-Suppression on numpy corners shaped:
      3xN [x_i,y_i,conf_i]^T
  
    Algo summary: Create a grid sized HxW. Assign each corner location a 1, rest
    are zeros. Iterate through all the 1's and convert them either to -1 or 0.
    Suppress points by setting nearby values to 0.
  
    Grid Value Legend:
    -1 : Kept.
     0 : Empty or suppressed.
     1 : To be processed (converted to either kept or supressed).
  
    NOTE: The NMS first rounds points to integers, so NMS distance might not
    be exactly dist_thresh. It also assumes points are within image boundaries.
  
    Inputs
      in_corners - 3xN numpy array with corners [x_i, y_i, confidence_i]^T.
      H - Image height.
      W - Image width.
      dist_thresh - Distance to suppress, measured as an infinty norm distance.
    Returns
      nmsed_corners - 3xN numpy matrix with surviving corners.
      nmsed_inds - N length numpy vector with surviving corner indices.
    """
    grid = np.zeros((H, W)).astype(int) # Track NMS data.
    inds = np.zeros((H, W)).astype(int) # Store indices of points.
    # Sort by confidence and round to nearest int.
    inds1 = np.argsort(-in_corners[2,:])
    corners = in_corners[:,inds1]
    rcorners = corners[:2,:].round().astype(int) # Rounded corners.
    # Check for edge case of 0 or 1 corners.
    if rcorners.shape[1] == 0:
      return np.zeros((3,0)).astype(int), np.zeros(0).astype(int)
    if rcorners.shape[1] == 1:
      out = np.vstack((rcorners, in_corners[2])).reshape(3,1)
      return out, np.zeros((1)).astype(int)
    # Initialize the grid.
    for i, rc in enumerate(rcorners.T):
      grid[rcorners[1,i], rcorners[0,i]] = 1
      inds[rcorners[1,i], rcorners[0,i]] = i
    # Pad the border of the grid, so that we can NMS points near the border.
    pad = dist_thresh
    grid = np.pad(grid, ((pad,pad), (pad,pad)), mode='constant')
    # Iterate through points, highest to lowest conf, suppress neighborhood.
    count = 0
    for i, rc in enumerate(rcorners.T):
      # Account for top and left padding.
      pt = (rc[0]+pad, rc[1]+pad)
      if grid[pt[1], pt[0]] == 1: # If not yet suppressed.
        grid[pt[1]-pad:pt[1]+pad+1, pt[0]-pad:pt[0]+pad+1] = 0
        grid[pt[1], pt[0]] = -1
        count += 1
    # Get all surviving -1's and return sorted array of remaining corners.
    keepy, keepx = np.where(grid==-1)
    keepy, keepx = keepy - pad, keepx - pad
    inds_keep = inds[keepy, keepx]
    out = corners[:, inds_keep]
    values = out[-1, :]
    inds2 = np.argsort(-values)
    out = out[:, inds2]
    out_inds = inds1[inds_keep[inds2]]
    return out, out_inds

  def run(self, img):
    """ Process a numpy image to extract points and descriptors.
    Input
      img - HxW numpy float32 input image in range [0,1].
    Output
      corners - 3xN numpy array with corners [x_i, y_i, confidence_i]^T.
      desc - 256xN numpy array of corresponding unit normalized descriptors.
      heatmap - HxW numpy heatmap in range [0,1] of point confidences.
      """
    assert img.ndim == 2, 'Image must be grayscale.'
    assert img.dtype == np.float32, 'Image must be float32.'
    H, W = img.shape[0], img.shape[1]
    inp = img.copy()
    inp = (inp.reshape(1, H, W))
    inp = torch.from_numpy(inp)
    inp = torch.autograd.Variable(inp).view(1, 1, H, W)
    if self.cuda:
      inp = inp.cuda()
    # Forward pass of network.
    outs = self.net.forward(inp)
    semi, coarse_desc = outs[0], outs[1]
    # Convert pytorch -> numpy.
    semi = semi.data.cpu().numpy().squeeze()
    # --- Process points.
    dense = np.exp(semi) # Softmax.
    dense = dense / (np.sum(dense, axis=0)+.00001) # Should sum to 1.
    # Remove dustbin.
    nodust = dense[:-1, :, :]
    # Reshape to get full resolution heatmap.
    Hc = int(H / self.cell)
    Wc = int(W / self.cell)
    nodust = nodust.transpose(1, 2, 0)
    heatmap = np.reshape(nodust, [Hc, Wc, self.cell, self.cell])
    heatmap = np.transpose(heatmap, [0, 2, 1, 3])
    heatmap = np.reshape(heatmap, [Hc*self.cell, Wc*self.cell])
    xs, ys = np.where(heatmap >= self.conf_thresh) # Confidence threshold.
    if len(xs) == 0:
      return np.zeros((3, 0)), None, None
    pts = np.zeros((3, len(xs))) # Populate point data sized 3xN.
    pts[0, :] = ys
    pts[1, :] = xs
    pts[2, :] = heatmap[xs, ys]
    pts, _ = self.nms_fast(pts, H, W, dist_thresh=self.nms_dist) # Apply NMS.
    inds = np.argsort(pts[2,:])
    pts = pts[:,inds[::-1]] # Sort by confidence.
    # Remove points along border.
    bord = self.border_remove
    toremoveW = np.logical_or(pts[0, :] < bord, pts[0, :] >= (W-bord))
    toremoveH = np.logical_or(pts[1, :] < bord, pts[1, :] >= (H-bord))
    toremove = np.logical_or(toremoveW, toremoveH)
    pts = pts[:, ~toremove]
    # --- Process descriptor.
    D = coarse_desc.shape[1]
    if pts.shape[1] == 0:
      desc = np.zeros((D, 0))
    else:
      # Interpolate into descriptor map using 2D point locations.
      samp_pts = torch.from_numpy(pts[:2, :].copy())
      samp_pts[0, :] = (samp_pts[0, :] / (float(W)/2.)) - 1.
      samp_pts[1, :] = (samp_pts[1, :] / (float(H)/2.)) - 1.
      samp_pts = samp_pts.transpose(0, 1).contiguous()
      samp_pts = samp_pts.view(1, 1, -1, 2)
      samp_pts = samp_pts.float()
      if self.cuda:
        samp_pts = samp_pts.cuda()
      desc = torch.nn.functional.grid_sample(coarse_desc, samp_pts, align_corners=True)
      desc = desc.data.cpu().numpy().reshape(D, -1)
      desc /= np.linalg.norm(desc, axis=0)[np.newaxis, :]
    return pts, desc, heatmap

def d2r(x):
    x = x * math.pi / 180.0
    if x > math.pi:
        x -= math.pi
    return x

def color_map(i):
    colors = [
        [255,0,0],
        [0,255,0],
        [0,0,255],
        [128,128,0],
        [0,128,128]
    ]

    if i < 5:
        return colors[i]
    else:
        return np.random.randint(0,256,3)

def draw_super_points(filepath,pts):
    image = cv2.imread(filepath,cv2.IMREAD_COLOR)
    i=0
    for pt in pts:
        color = color_map(i)
        center = [pt[1], pt[0]]
        image = draw_circle(image, center, color)
        i+=1
    return image

def draw_circle(image, center, color,  radius = 4, border_color = [255,255,255]):
    image_p = np.pad(image, ((radius,radius),(radius,radius),(0,0)),'constant')
    center_p = [center[0]+radius, center[1]+radius]
    edge_d = math.floor((2*radius + 1)/6)
    image_p[center_p[0]-radius, (center_p[1]-edge_d):(center_p[1]+edge_d+1), :] = np.tile(border_color,[3,1])
    image_p[center_p[0]+radius, (center_p[1]-edge_d):(center_p[1]+edge_d+1), :] = np.tile(border_color,[3,1])
    for i in range(1,radius):
        image_p[center_p[0]+i, center_p[1]-radius+i-1, :] = border_color
        image_p[center_p[0]-i, center_p[1]-radius+i-1, :] = border_color
        image_p[center_p[0]+i, (center_p[1]-radius+i):(center_p[1]+radius-i+1), :] = np.tile(color, [2*(radius-i)+1,1])
        image_p[center_p[0]-i, (center_p[1]-radius+i):(center_p[1]+radius-i+1), :] = np.tile(color, [2*(radius-i)+1,1])
        image_p[center_p[0]+i, center_p[1]+radius+1-i, :] = border_color
        image_p[center_p[0]-i, center_p[1]+radius+1-i, :] = border_color

    image_p[center_p[0], center_p[1]-radius, :] = border_color
    image_p[center_p[0], (center_p[1]-radius+1):(center_p[1]+radius), :] = np.tile(color, [2*(radius-1)+1,1])
    image_p[center_p[0], center_p[1]+radius, :] = border_color

    return image_p[radius:image_p.shape[0]-radius, radius:image_p.shape[1]-radius, :]

def super_points_single_example():

    impath = 'office/seq-02/frame-000052.color.jpg'
    ckpt_path = "./bin/superpoint_v1.pth"
    print(impath)
    scale_factor = 1 #4，2，1
    nms = 9 #4，9，19； 4*scale_factor+4/scale_factor-1
    padding = 0  # 2,1,0
    conf  = 0.015
    H = 480
    W = 640
    img_size = [H//scale_factor,W//scale_factor]

    print('==> Loading pre-trained network.')
    # This class runs the SuperPoint network and processes its outputs.
    fe = SuperPointFrontend(weights_path=ckpt_path,
                            nms_dist=nms,
                            conf_thresh=conf,
                            nn_thresh=.7,
                            cuda=False)
    print('==> Successfully loaded pre-trained network.')

    grayim = cv2.imread(impath, 0)
    if grayim is None:
        raise Exception('Error reading image %s' % impath)
    # Image is resized via opencv.
    interp = cv2.INTER_AREA
    grayim = cv2.resize(grayim, (img_size[1], img_size[0]), interpolation=interp)
    img = (grayim.astype('float32') / 255.)
    pts, desc, heatmap = fe.run(img)
    sps = np.round(pts.T*scale_factor)[:,:2].astype(int)
    sps += np.array([padding,padding])

    print('num of point:',sps.shape[0])
    img = draw_super_points(impath, sps)
    cv2.imshow("superpoint_dense", img)

    '''ip_num=0
    ind = []
    coord = np.load(impath.replace('color', 'coord_cali').replace('png', 'npy')).astype(np.float32)
    for id, ip in enumerate(sps):
        patch_center = np.array([ip[1], ip[0]])  # u,v to x,y axis
        radius = 63//2
        right_bottom = patch_center + radius
        left_top = patch_center - radius
        is_outside = True if right_bottom[0] >= H or right_bottom[1] >= W or left_top[0] < 0 or left_top[
            1] < 0 else False
        if is_outside: continue
        if np.linalg.norm(coord[patch_center[0], patch_center[1], :]) == 0:
            continue

        # record image id, patch id.
        ip_num += 1
        ind += [id]
    sps = sps[ind]

    print('num of point:',sps.shape[0])
    img = draw_super_points(impath, sps)
    cv2.imshow("superpoint", img)'''
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # cv2.imwrite('superpoint_'+str(scale_factor)+'-'+str(nms)+'.png', img)

def superpoint(image):
    global fe
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    pts, desc, heatmap = fe.run(gray_image)
    print(np.max(pts[0]), np.max(pts[1]))
    print(pts.shape, desc.shape, heatmap.shape, gray_image.shape)
    desc = desc.T
    return pts, np.array([np.maximum(np.minimum(np.floor(desc[x] * 1500), 255), 0) for x in range(desc.shape[0])], dtype=np.uint8)

def write_to_key(name, kp, des):
    with open(name + '.key', 'w', encoding='utf-8') as f:
        f.write('{} 256\n'.format(kp.shape[1]))
        for i in range(kp.shape[1]):
            f.write('{:.2f} {:.2f} -1. -1.\n'.format(kp[1][i], kp[0][i]))
            for j in range(256):
                f.write(' {}'.format(des[i][j]))
            f.write('\n')
            
if 0:#__name__ == "__main__":
    super_points_single_example()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=str, default='.')
    parser.add_argument('--model_path', type=str, default='bin/superpoint_v1.pth')
    args = parser.parse_args()
    # print('==> Loading pre-trained network.')
    fe = SuperPointFrontend(weights_path=args.model_path,
                            nms_dist=4,
                            conf_thresh=0.010,
                            nn_thresh=0.7,
                            cuda=False)
    # print('==> Successfully loaded pre-trained network.')
    for img_name in os.listdir(args.directory):
        if len(img_name) > 4 and img_name[-4:] == '.jpg':
            print(img_name)
            img = cv2.imread(args.directory + '/' + img_name)
            a, b = superpoint(img)
            write_to_key(args.directory + '/' + img_name[:-4], a, b)
