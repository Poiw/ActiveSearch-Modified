#ifndef FEATURE_LOADER_HH
#define FEATURE_LOADER_HH

#include <vector>
#include <iostream>
#include <fstream>
#include <cmath>
#include <cstdint>

namespace feature {
    const int dim = 256;
}

enum FEATURE_FORMAT {
    LOWE = 0,
    UNDEFINED = 3
};

struct feature_keypoint {
    float x, y, scale, orientation;
    feature_keypoint( )
	{
	  x = y = scale = orientation = 0.0;
	}
	
	feature_keypoint( float x_, float y_, float scale_, float orientation_ )
	{
	  x = x_;
	  y = y_;
	  scale = scale_;
	  orientation = orientation_;
	}
};


class feature_loader
{
  public:
    //! constructor
    feature_loader( );
    
    //! destructor
    ~feature_loader( );
	
    //! load features from a file with a given format
    void load_features( const char *filename, FEATURE_FORMAT format, uint32_t hint_dim = 0 );
	
    //! save the features loaded to a file in David Lowes Format
    bool save_features_lowe( const char *filename );
    
    //! clears all data loaded so far
    void clear_data( );
	
    //! returns the number of features loaded
    uint32_t get_nb_features( );
    
    //! get access to a vector containg the descriptors (stored as chars)
    std::vector< unsigned char* >& get_descriptors( );
    
    //! get the keypoints
    std::vector< feature_keypoint >& get_keypoints( );
	
  private:
    
    std::vector< feature_keypoint > mKeypoints;
    std::vector< unsigned char* > mDescriptors;
    uint32_t mNbFeatures, dim;
    
    bool load_Lowe_features( const char *filename, uint32_t hint_dim );
  
};





#endif
