#include "feature_loader.hh"


feature_loader::feature_loader( )
{
  mNbFeatures = 0;
  dim = 0;
  mKeypoints.clear();
  mDescriptors.clear();
}

feature_loader::~feature_loader( )
{
  clear_data( );
}
    
void feature_loader::load_features( const char *filename, FEATURE_FORMAT format, uint32_t hint_dim )
{
  clear_data( );
  bool loaded = load_Lowe_features( filename, hint_dim );
  
  if( !loaded )
    std::cerr << "Could not load the features from the given file " << filename << std::endl;
}

bool feature_loader::save_features_lowe( const char *filename )
{
  //now open the .feature file and read out the interest points
  // format:
  //
  // nb_keypoints size_descriptor (should be 128)
  // for each keypoint:
  //	y x scale orientation(radians) 
  //    descripor( size_descriptor many unsigned char values) (6 lines with 20 values, 1 with 8 values)
  //the coordinates of the interest points are stored in a coordinate system in which the origin corresponds to the upper left of the image
  
  std::ofstream outstream( filename, std::ios::out );
  
  if ( !outstream.is_open() )
    return false;
  
  // save the number of keypoints and the size of the descriptors
  outstream << mNbFeatures << " " << dim << std::endl;
  
  // load the keypoints and their descriptors
  for( uint32_t i=0; i<mNbFeatures; ++i )
  {
    outstream << mKeypoints[i].y << " " << mKeypoints[i].x << " " << mKeypoints[i].scale << " " << mKeypoints[i].orientation << std::endl;
    
    outstream << (int) mDescriptors[i][0] << " ";
    for( int j=1; j<dim; ++j )
    {
      if( j%20 == 0 )
		outstream << std::endl;
	  outstream << (int) mDescriptors[i][j] << " ";
    }
    outstream << std::endl;
  }
  
  outstream.close();
  
  return true;
}


void feature_loader::clear_data( )
{
  for( uint32_t i=0; i<mNbFeatures; ++i )
  {
    if( mDescriptors[i] != 0 )
      delete [] mDescriptors[i];
    mDescriptors[i] = 0;
  }
  mKeypoints.clear();
  mDescriptors.clear();
}
    
uint32_t feature_loader::get_nb_features( )
{
  return mNbFeatures;
}

std::vector< unsigned char* >& feature_loader::get_descriptors( )
{
  return mDescriptors;
}

std::vector< feature_keypoint >& feature_loader::get_keypoints( )
{
  return mKeypoints;
}
    

bool feature_loader::load_Lowe_features( const char *filename, uint32_t hint_dim )
{
  //now open the .feature file and read out the interest points
  // format:
  //
  // nb_keypoints size_descriptor (should be 128)
  // for each keypoint:
  //	y x scale orientation(radians) 
  //    descripor( size_descriptor many char values) (6 lines with 20 values, 1 with 8 values)
  //the coordinates of the interest points are stored in a coordinate system in which the origin corresponds to the upper left of the image
  
  std::ifstream instream( filename, std::ios::in );
  
  if ( !instream.is_open() )
    return false;
  
  // read the number of keypoints and the size of the descriptors
  uint32_t size_descriptor;
  instream >> mNbFeatures >> size_descriptor;
  
  if( hint_dim && size_descriptor != hint_dim )
    return false;

  dim = size_descriptor;
  
  // load the keypoints and their descriptors
  mKeypoints.resize(mNbFeatures);
  mDescriptors.resize(mNbFeatures,0);
  
  double x,y,scale,orientation;
  unsigned int descriptor_element;
  
  for( uint32_t i=0; i<mNbFeatures; ++i )
  {
    mDescriptors[i] = new unsigned char[dim];
    instream >> y >> x >> scale >> orientation;
    mKeypoints[i] = feature_keypoint( x, y, scale, orientation );
    
    // read the descriptor
    for( int j=0; j<dim; ++j )
    {
      instream >> descriptor_element;
      mDescriptors[i][j] = (unsigned char) descriptor_element;
    }
  }
  
  instream.close();
  
  return true;
}