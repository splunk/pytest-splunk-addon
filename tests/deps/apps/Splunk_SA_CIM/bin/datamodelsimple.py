import splunk.Intersplunk
import sys

from splunk import AuthenticationFailed
from splunk.clilib.bundle_paths import make_splunkhome_path
sys.path.append(make_splunkhome_path(["etc", "apps", "Splunk_SA_CIM", "lib"]))
from cim_models import DataModels
from splunk_sa_cim.log import setup_logger

logger = setup_logger('datamodelsimple')


if __name__ == '__main__':
    logger.info('Starting datamodelsimple search command')

    return_type = 'models'
    datamodel = None
    obj = None
    nodename = None

    # Override Defaults w/ opts below
    if len(sys.argv) > 1:
        for a in sys.argv:
            if a.startswith('type='):
                where = a.find('=')
                return_type = a[where + 1:len(a)]
            elif a.startswith('datamodel='):
                where = a.find('=')
                datamodel = a[where + 1:len(a)]
            elif a.startswith('object='):
                where = a.find('=')
                obj = a[where + 1:len(a)]
            elif a.startswith('nodename='):
                where = a.find('=')
                nodename = a[where + 1:len(a)]

    # if nodename is specified, create obj
    if nodename and not obj:
        obj = nodename.split('.')
        obj = obj[-1]

    results, dummyresults, settings = splunk.Intersplunk.getOrganizedResults()
    results = []  # we don't care about incoming results

    sessionKey = settings.get('sessionKey', False)

    try:
        # validate sessionKey
        if not sessionKey:
            raise AuthenticationFailed

        if return_type == 'models':
            models = DataModels.getDatamodelList(sessionKey)
            results = [{'datamodel': i} for i in models]

        elif return_type == 'objects':
            if datamodel:
                objects = DataModels.getDatamodelObjectList(
                    datamodel, sessionKey)
                modelJson = DataModels.getDatamodelJson(datamodel, sessionKey)
                results = [
                    {
                        'object': i,
                        'lineage': DataModels.getObjectLineage(
                            i, modelJson=modelJson)
                    }
                    for i in objects
                ]
            else:
                e = 'Must specify datamodel for type: objects'
                logger.error(e)
                results = splunk.Intersplunk.generateErrorResults(e)

        elif return_type == 'attributes':
            if datamodel and obj:
                # get the model
                modelJson = DataModels.getDatamodelJson(datamodel, sessionKey)
                # getAvailableFields for non-transforming search
                availableFieldsMap = DataModels.getAvailableFieldsMap(
                    obj, modelJson)
                # if we were able to determine lineage extend fields
                if availableFieldsMap is not None:
                    for lineage_field, field in availableFieldsMap.items():
                        results.append(
                            {'attribute': field, 'lineage': lineage_field})
                else:
                    e = "Could not determine lineage for datamodel: %s, object: %s" % (
                        datamodel, obj)
                    logger.error(e)
                    raise Exception(e)

            else:
                e = 'Must specify datamodel and object for type: attributes'
                logger.error(e)
                results = splunk.Intersplunk.generateErrorResults(e)

    except Exception as e:
        logger.error(e)
        results = splunk.Intersplunk.generateErrorResults(str(e))

    splunk.Intersplunk.outputResults(results)
    logger.info('Finishing datamodelinfo search command')
