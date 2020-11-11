/*===========================================================================*\
 *                                                                           *
 *                            ACG Localizer                                  *
 *      Copyright (C) 2011 by Computer Graphics Group, RWTH Aachen           *
 *                           www.rwth-graphics.de                            *
 *                                                                           *
 *---------------------------------------------------------------------------* 
 *  This file is part of ACG Localizer                                       *
 *                                                                           *
 *  ACG Localizer is free software: you can redistribute it and/or modify    *
 *  it under the terms of the GNU General Public License as published by     *
 *  the Free Software Foundation, either version 3 of the License, or        *
 *  (at your option) any later version.                                      *
 *                                                                           *
 *  ACG Localizer is distributed in the hope that it will be useful,         *
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of           *
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            *
 *  GNU General Public License for more details.                             *
 *                                                                           *
 *  You should have received a copy of the GNU General Public License        *
 *  along with ACG Localizer.  If not, see <http://www.gnu.org/licenses/>.   *
 *                                                                           *
\*===========================================================================*/ 

#include <vector>
#include <set>
#include <iostream>
#include <fstream>
#include <stdint.h>
#include <string>
#include <cmath>
#include <algorithm>
#include <climits>
#include <sstream>

#include "sfm/parse_bundler.hh"

const uint32_t sift_dim = feature::dim;

int main (int argc, char **argv)
{
  if( argc != 4 )
  {
    std::cout << "_______________________________________________________________________________________________________" << std::endl;
    std::cout << " -                                                                                                   - " << std::endl;
    std::cout << " -    Bundle2Info - Extract camera and feature information from Bundler output files, save feature   - " << std::endl;
	std::cout << " -                  information (including descriptors) in binary file.                              - " << std::endl;
    std::cout << " -                               2011 by Torsten Sattler (tsattler@cs.rwth-aachen.de)                - " << std::endl;
    std::cout << " -                                                                                                   - " << std::endl;
    std::cout << " - usage: Bundle2Info bundler_output image_list outfile                                              - " << std::endl;
    std::cout << " - Parameters:                                                                                       - " << std::endl;
    std::cout << " -  bundler_output                                                                                   - " << std::endl;
    std::cout << " -     Filename of an output file (usually called bundle.out) generated by Bundler.                  - " << std::endl; 
    std::cout << " -                                                                                                   - " << std::endl;
    std::cout << " -  image_list                                                                                       - " << std::endl;
    std::cout << " -     Text file containing the list of images (and their paths relative to the list file)           - " << std::endl;
    std::cout << " -     used by Bundler (usually called list.txt). Notice that the program will try to load the       - " << std::endl;
	std::cout << " -     .key files containing the SIFT-features by simply changing the ending of the image names      - " << std::endl;
	std::cout << " -     from .jpg to .key, using the filenames specified in the list to load the files.               - " << std::endl;
    std::cout << " -                                                                                                   - " << std::endl;
    std::cout << " -  outfile                                                                                          - " << std::endl;
    std::cout << " -     The output generated by Bundle2Info. It is a binary file of the following structure:          - " << std::endl;
    std::cout << " -     number of cameras (uint32_t)                                                                  - " << std::endl;
    std::cout << " -     number of points (uint32_t)                                                                   - " << std::endl;
    std::cout << " -     for every point:                                                                              - " << std::endl;
    std::cout << " -     3D coordinates (float) number of images this point is visible in (uint32_t)                   - " << std::endl;
    std::cout << " -     for every such image: camera id (uint32_t) 2D coordinates scale orientation (floats)          - " << std::endl;
    std::cout << " -     descriptor (unsigned char)                                                                    - " << std::endl;
    std::cout << " -                                                                                                   - " << std::endl;
    std::cout << "_______________________________________________________________________________________________________" << std::endl;
    return 1;
  }
  
  ////
  // get the data from bundler
  
  std::cout << "-> parsing bundler data " << std::endl;
  parse_bundler parser;
  if( !parser.parse_data( argv[1], argv[2] ) )
  {
    std::cerr << "ERROR: could not parse the information from bundler " << std::endl;
    return 1;
  }
  
  // get the parsed information
  std::vector< feature_3D_info >& feature_infos = parser.get_feature_infos();
  
  uint32_t nb_cameras = parser.get_number_of_cameras();
  uint32_t nb_points = parser.get_number_of_points();
  std::cout << "--> done parsing the bundler output " << std::endl;
  
  /////
  // do some statistics:
  // average number of features per camera
  // average number of cameras a 3D point is visible in
  std::vector< uint32_t > nb_features_per_cam( nb_cameras, 0 );
  
  double average_cams_per_feature = 0.0;
  uint32_t max_cams_per_feature = 0.0;
  
  for( uint32_t i=0; i<nb_points; ++i )
  {
    for( uint32_t j=0; j< (uint32_t) feature_infos[i].view_list.size(); ++j )
      nb_features_per_cam[feature_infos[i].view_list[j].camera]+=1;
	
    average_cams_per_feature += (double) feature_infos[i].view_list.size();
    max_cams_per_feature = (max_cams_per_feature > (feature_infos[i].view_list.size()))? max_cams_per_feature:(feature_infos[i].view_list.size());
	
  }
  
  average_cams_per_feature /= double(nb_points);
  
  double average_features_per_cams = 0.0;
  uint32_t max_features_per_cam = 0;
  uint32_t min_features_per_cam = UINT_MAX;
  
  for( uint32_t i=0; i<nb_cameras; ++i )
  {
    average_features_per_cams += double(nb_features_per_cam[i]);
    max_features_per_cam = (max_features_per_cam > nb_features_per_cam[i] )? max_features_per_cam:nb_features_per_cam[i];
    min_features_per_cam = (min_features_per_cam < nb_features_per_cam[i] )? min_features_per_cam:nb_features_per_cam[i];
  }
  average_features_per_cams /= double(nb_cameras);
  
  std::cout << std::endl << "############# Statistics #############" << std::endl;
  std::cout << " # 3D points " << nb_points << ", # cameras " << nb_cameras << std::endl;
  std::cout << " a single 3D point is on average visible in " << average_cams_per_feature << " cameras ( max: " << max_cams_per_feature << " ) " << std::endl;
  std::cout << " min #points in image " << min_features_per_cam << ", average: " << average_features_per_cams << ", max: " << max_features_per_cam << std::endl;
  std::cout << "######################################" << std::endl << std::endl;
  
  ////
  // save all data
  std::cout << "->saving the information from bundler to " << argv[3] << std::endl;
  
  std::ofstream ofs( argv[3], std::ios::out | std::ios::binary );
    
  if( !ofs.is_open() )
  {
    std::cerr << " Could not write information " << argv[3] << std::endl;
    return 1;
  }
  
  // write out the number of cameras and points
  ofs.write( (char*) &nb_cameras, sizeof( uint32_t) );
  ofs.write( (char*) &nb_points, sizeof( uint32_t ) );
  
  // write out the points
  for( uint32_t i=0; i<nb_points; ++i )
  {
	// first the 3D position
    float *pos = new float[3];
    pos[0] = feature_infos[i].point.x;
    pos[1] = feature_infos[i].point.y;
    pos[2] = feature_infos[i].point.z;
    ofs.write( (char*) pos, 3*sizeof( float ) );
	delete [] pos;
	
	// the number of cameras that point is visible in
    uint32_t nb_cams_visible_in = (uint32_t) feature_infos[i].view_list.size();
    ofs.write( (char*) &nb_cams_visible_in, sizeof( uint32_t ) );
	
	// for every camera: the keypoint data and the descriptor
    for( uint32_t j=0; j<nb_cams_visible_in; ++j )
    {
      uint32_t cam = feature_infos[i].view_list[j].camera;
      float x = feature_infos[i].view_list[j].x;
      float y = feature_infos[i].view_list[j].y;

      float scale = feature_infos[i].view_list[j].scale;
      float orientation = feature_infos[i].view_list[j].orientation;

	  unsigned char *desc = new unsigned char[sift_dim];
      for( uint32_t k=0; k<sift_dim; ++k )
		desc[k] = feature_infos[i].descriptors[sift_dim*j+k];
      
      ofs.write( (char*) &cam, sizeof( uint32_t ) );
      ofs.write( (char*) &x, sizeof( float ) );
      ofs.write( (char*) &y, sizeof( float ) );
      ofs.write( (char*) &scale, sizeof( float ) );
      ofs.write( (char*) &orientation, sizeof( float ) );
      ofs.write( (char*) desc, sift_dim*sizeof( unsigned char ) );
      
      delete [] desc;
    }
    
    
  }
  
  ofs.close();
  std::cout << "--> done" << std::endl;
  
  return 0;
}