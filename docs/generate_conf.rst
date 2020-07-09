Generate Conf Utility
======================

.. _generate_conf:

Overview
""""""""""

* The utility helps in creating the `pytest-splunk-addon-data-generator.conf` from the existing `eventgen.conf` of the add-on.
* The utility adds the following metadata required for the index-times tests in the new conf file:

    * input_type
    * host_type
    * timestamp_type
    * expected_event_count
    * sourcetype_to_search

* All of these above metadata will be appended with keyword 'REVIEW', indicating that these values will have to be filled by the
  user, depending on the requirements of the add-on.

* The utility reads the tokens in the existing `eventgen.conf` and identifies if it can be replaced with any of 
  the new token replacement settings. The new token replacement settings are as follows:

    * src
    * dest
    * src_port
    * dest_port
    * dvc
    * host
    * url

* As all the above mentioned new replacement settings are for key_fields, a new parameter will also be added i.e `token.n.field`
* The new token replacement settings and field parameter will be appended with keyword 'REVIEW', indicating the user will have to check
  for the following:

    1. If the new token replacement settings are applicable for the addon. If yes, then the user will have to fill the appropriate values as mentioned in the spec file.
    2. If the field provided in the 'token.n.field', is extracted in the add-on or not. If the field is not extracted, 
       the parameter 'token.n.field' should be removed.

    
How to generate the new conf file?
"""""""""""""""""""""""""""""""""""

    * Execute the following command:

        .. code-block:: console

            generate-indextime-conf <path-to-addon> [<path-to-the-new-conf-file>]

        For example:

        .. code-block:: console

            generate-indextime-conf SampleTA SampleTA/default/pytest-splunk-addon-data-generator.conf        


    .. note::
        Add-on must contain samples folder, for the utility to work properly.
