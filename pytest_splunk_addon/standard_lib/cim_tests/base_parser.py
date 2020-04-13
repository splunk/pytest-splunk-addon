from abc import ABC, abstractclassmethod

class BaseParser(ABC):
    """
    Abstract class to parse the Data model files. 
    The possible format can be Json, YML, csv, Cim_json
    """

    @abstractclassmethod
    def parse_data_model(cls, file_path):
        """
        Parse the DataModel file
        Convert it to JSON

        Expected Output: \n
            {
                "name":"Default_Authentication",
                "tags": ["authentication","default"],
                "fields_cluster":[],     
                "fields":[
                    {     
                        "fieldname": "action",     
                        "field_type": "required",    
                        "condition": "action IN ('success','failure','error')",
                        "comment":"The action performed on the resource."
                    },
                    ],
                "child_dataset": [
                    {
                        "name":"SuccessFul_Default_Authentication",
                        "tags": ["authentication","default"],
                        "fields_cluster":[],
                        "fields":[]
                        "child_dataset":[],
                        "search_constraints": "action='success'"
                    }
                ],
                "search_constraints":"action='failure'"
            }
        """
        pass