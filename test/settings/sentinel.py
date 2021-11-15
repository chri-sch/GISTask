evalscript_all_bands = """
    //VERSION=3
    function setup() {
        return {
            input: [{
                bands: ["B01","B02","B03","B04","B05","B06","B07","B08","B8A","B09","B11","B12"],
                units: "DN"
            }],
            output: {
                bands: 12,
                sampleType: "AUTO",
                noDataValue: -9999,
            }
        };
    }

    function evaluatePixel(sample) {
        return [sample.B01,
                sample.B02,
                sample.B03,
                sample.B04,
                sample.B05,
                sample.B06,
                sample.B07,
                sample.B08,
                sample.B8A,
                sample.B09,
                sample.B11,
                sample.B12];
    }
"""


eval_script_sentinel_1 = """
    //VERSION=3
    function setup() {
      return {
        input: [
          {
            bands: ["VV","VH"],                  
          }
        ],
        output: [
          {
            id: "default",
            bands: 2,
            sampleType: "AUTO",        
            noDataValue: -9999,
          },    
        ],
        mosaicking: "SIMPLE",
      };
    }
    
    
    function evaluatePixel(samples) {
        // Your javascript code here
        return {
          default: [],
        };
      }

"""