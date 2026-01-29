
param._cam = <json>
    * Json specification for classifying response actions.
    * See Appendix A.
    * Optional.
    * Defaults to None.

param._cam_workers = <json>
    * Json specification for defining remote workers.
    * See Appendix B.
    * Optional.
    * Defaults to None.


###### Appendix A: Common Action Model Specification #######
## category:          The category or categories the modular action belongs to.
##                    Required.
##                    For instance, "Information Gathering".
##                    See cam_categories.csv for recommended values.
## task:              The function or functions performed by the modular action.
##                    Required.
##                    For instance, "create".
##                    See cam_tasks.csv for recommended values.
## subject:           The object or objects that the modular action's task(s)
##                    can be performed on (i.e. "endpoint.file").
##                    Required.
##                    See cam_subjects.csv for recommended values.
## technology:        The technology or technologies that the modular action supports.
##                    Required.
##                    vendor:  The vendor of the technology.
##                        Required.
##                        For instance, "Splunk".
##                    product: The product of the technology.
##                        Required.
##                        For instance, "Enterprise".
##                    version: The version or versions of the technology.
##                        Optional.
##                        For instance, "6.4".
## drilldown_uri:     Specifies a custom target for viewing the events
##                    outputted as a result of the action.
##                    Custom target can specify app and/or view depending on syntax.
##                    Optional.
##                    For instance, "my_view?form.orig_sid=$sid$&form.orig_rid=$rid$"
##                    For instance, "../my_app/my_view?form.orig_sid=$sid$&form.orig_rid=$rid$"
## field_name_params: The param or params which represent the name of a result field.
##                    Optional.
##                    For instance, ["param.search_field"] indicates that the value of "param.search_field"
##                    should be present as a field in the result or results being operated on.
## required_params:   Parameter(s) required for successful action execution. 
##                    Indicated by "*" in the custom alert action user interface. 
##                    For instance, ["param.search_field"] indicates that "param.search_field"
##                    should be specified when submitting the action on the custom alert action
##                    user interface.
##                    Optional.
## supports_adhoc:    Specifies if the modular action supports adhoc invocations.
##                    Optional.
##                    Defaults to False.
## supports_cloud:    Specifies if the modular actions supports the "cloud" model.
##                    For instance, does the action function properly when the search head does not have access
##                    to the local network.
##                    Optional.
##                    Defaults to True.
## supports_workers:  Specifies if the modular actions supports remote workers.
##                    supports_workers==True implies supports_cloud==True
##                    Optional.
##                    Defaults to False.
#{
#    "category":          ["<category>", ..., "<category">],
#    "task":              ["<task>", ..., "<task>"],
#    "subject":           ["<subject>", ..., "<subject>"],
#    "technology":        [{ "vendor":  "<vendor>",
#                            "product": "<product>",
#                            "version": ["<version>", ..., "<version>"]
#                          },
#                          ...,
#                          { "vendor":  "<vendor>",
#                            "product": "<product>",
#                            "version": ["<version>", ..., "<version>"]
#                          }
#                         ],
#    "drilldown_uri":     "<uri>",
#    "field_name_params": ["<param.param1>", ..., "<param.paramN>"],
#    "required_params":   ["<param.param1>", ..., "<param.paramN>"]
#    "supports_adhoc":    true | false,
#    "supports_cloud":    true | false,
#    "supports_workers":  true | false
#}


###### Appendix B: Common Action Model Remote Workers Specification #######
## List of Splunk "serverName" values as advertised by /server/info
##
## Special "serverName" values:
##    * "local" - action script will continue doing work locally in addition to
##                queueing work for additional workers (if specified).
##                
##
## [ "local"?, "worker1", "worker2", ..., "workern" ]