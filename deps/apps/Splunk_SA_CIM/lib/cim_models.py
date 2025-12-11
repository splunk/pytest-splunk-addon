"""
Copyright (C) 2005 - 2019 Splunk Inc. All Rights Reserved.
"""
import json
import splunk.rest as rest

try:
    from urllib.request import quote
except ImportError:
    from urllib import quote

# Python 2+3 basestring
try:
    basestring
except NameError:
    basestring = str


class DataModels(object):
    """ Class for data model utilities """
    baseObjects = ['BaseEvent', 'BaseSearch', 'BaseTransaction']
    # per SOLNESS-5244: this list should only include fields avail to
    # both | datamodel and | tstats with the exception of _raw
    baseEventAttributes = ['_time', '_raw', 'source', 'sourcetype', 'host']

    @staticmethod
    def getDatamodels(sessionKey, namespace='search', owner='nobody'):
        """ Return JSON specification for a given model
        @param sessionKey - A splunk session key
        @param namespace  - A splunk app context
        @param owner      - A splunk user context

        @return dict      - A python dictionary with datamodel specification contents

        @raise Exception  - Raises "Could not parse|retrieve datamodel..."
        """
        getargs = {'output_mode': 'json', 'count': 0}
        uri = '/servicesNS/{0}/{1}/data/models/'.format(
            quote(owner, safe=''), quote(namespace, safe=''))
        r, c = rest.simpleRequest(uri, sessionKey=sessionKey, getargs=getargs)
        if r.status == 200:
            c = json.loads(c)['entry']
            datamodels = {}
            for x in c:
                try:
                    datamodels[x['name']] = json.loads(x['content']['eai:data'])
                except Exception:
                    pass
            return datamodels

        raise Exception('Could not retrieve datamodels from %s' % uri)

    @staticmethod
    def getDatamodelList(sessionKey, namespace='search', owner='nobody'):
        """ Return list of datamodels
        @param sessionKey - A splunk session key
        @param namespace  - A splunk app context
        @param owner      - A splunk user context

        @return list      - A list of datamodels

        @raise Exception  - Raises multiple exceptions
        """
        datamodels = DataModels.getDatamodels(sessionKey, namespace=namespace, owner=owner)
        return list(datamodels)

    @staticmethod
    def getDatamodelJson(datamodel, sessionKey, namespace='search', owner='nobody'):
        """ Return JSON specification for a given model
        @param datamodel  - The datamodel entity name
        @param sessionKey - A splunk session key
        @param namespace  - A splunk app context
        @param owner      - A splunk user context

        @return dict      - A python dictionary with datamodel specification contents

        @raise Exception  - Raises "Could not parse|retrieve datamodel..."
        """
        getargs = {'output_mode': 'json'}
        uri = '/servicesNS/{0}/{1}/data/models/{2}'.format(
            quote(owner, safe=''), quote(namespace, safe=''), quote(datamodel, safe=''))
        r, c = rest.simpleRequest(uri, sessionKey=sessionKey, getargs=getargs)
        if r.status == 200:
            return json.loads(json.loads(c)['entry'][0]['content']['eai:data'])

        raise Exception('Could not retrieve datamodel from %s' % uri)

    @staticmethod
    def getObjectLineage(objectName, modelJson, includeBaseObject=False, outputMode='basestring'):
        """ Return the lineage of an object
        @param objectName        - The name of the object
        @param modelJson         - The datamodel JSON specification
        @param includeBaseObject - Whether or not to root lineage at BaseEvent|BaseSearch
        @param outputMode        - Whether to output basestring|list

        @return lineage          - A lineage string or list
        """
        parents = {obj['objectName']: obj['parentName'] for obj in modelJson['objects']}
        lineage = []
        tmp = objectName

        if tmp in parents:
            while tmp in parents:
                lineage.append(tmp)
                tmp = parents[tmp]
            if includeBaseObject:
                lineage.append(tmp)
            lineage.reverse()
            if outputMode == 'list':
                return lineage
            else:
                return '.'.join(lineage)
        if outputMode == 'list':
            return []
        return ''

    @staticmethod
    def stripBaseObject(lineage, outputMode='basestring'):
        """ Remove the baseObject from a lineage string/list
        @param lineage    - A lineage string or list
        @param outputMode - Whether to output basestring|list

        @return lineage    - A lineage string or list
        """
        if len(lineage) > 0:
            if isinstance(lineage, basestring):
                lineage = lineage.split('.')
            if lineage[0] in DataModels.baseObjects:
                lineage.pop(0)
            if outputMode == 'list':
                return lineage
            else:
                return '.'.join(lineage)
        if outputMode == 'list':
            return []
        return ''

    @staticmethod
    def getDatamodelObjectList(datamodel, sessionKey, baseEventOnly=False, namespace='search', owner='nobody'):
        """ Return list of objects in a datamodel
        @param datamodel     - The datamodel entity name
        @param sessionKey    - A splunk session key
        @param baseEventOnly - Whether or not to whitelist BaseEvent objects
        @param namespace     - A splunk app context
        @param owner         - A splunk user context

        @return objects      - A list of objects

        @raise Exception     - Raises "Could not parse|retrieve datamodel..."
        """
        objects = []

        # get the model
        modelJson = DataModels.getDatamodelJson(datamodel, sessionKey, namespace, owner)

        for object in modelJson.get('objects', []):
            if object.get('objectName'):
                objectName = object['objectName']

                if baseEventOnly:
                    objectLineage = DataModels.getObjectLineage(
                        objectName, modelJson, includeBaseObject=True)
                    if objectLineage.startswith('BaseEvent'):
                        objects.append(objectName)
                else:
                    objects.append(objectName)

        return objects

    @staticmethod
    def getObjectAttributes(objectName, modelJson):
        """ Return a list of object specific attributes
        This method does NOT return attributes from it's parent(s)
        @param objectName  - The name of the object
        @param modelJson   - The datamodel JSON specification

        @return attributes - A list of attributes
        """
        attributes = []

        for obj in modelJson.get('objects', {}):
            if obj.get('objectName') == objectName:
                for field in obj.get('fields', []):
                    attributes.append(field.get('fieldName', []))
                for fields in [calc.get('outputFields') for calc in obj.get('calculations', {})]:
                    attributes.extend([field.get('fieldName', []) for field in fields])
                break

        return attributes

    @staticmethod
    def getAvailableFields(objectName, modelJson, flat=False):
        """ Return a list of all available object attributes
        Recurses through the object's parents (including the baseObject)
        @param objectName - The name of the object
        @param modelJson  - The datamodel JSON specification
        @param flat       - Whether to include attribute lineage or not

        @return None      - If lineage could not be established
        @return list      - A list of available fields
        """
        availableFieldsMap = DataModels.getAvailableFieldsMap(objectName, modelJson)

        if availableFieldsMap:
            if flat:
                availableFields = list(set(availableFieldsMap.values()))
            else:
                availableFields = list(availableFieldsMap)
        else:
            availableFields = None

        return availableFields

    @staticmethod
    def getAvailableFieldsMap(objectName, modelJson):
        """ Return a dictionary of all available object attributes
        Recurses through the object's parents (including the baseObject)
        @param objectName - The name of the object
        @param modelJson  - The datamodel JSON specification

        @return None      - If lineage could not be established
        @return dict      - A dictionary of available fields of the form
                            {'lineage.attribute': 'attribute'}
        """
        # 0.  initialize availableFields list
        availableFields = {}
        # 1. retrieve lineage
        lineage = DataModels.getObjectLineage(
            objectName, modelJson=modelJson, includeBaseObject=True, outputMode='list')
        # 2. length should be a non-zero length string
        if len(lineage) > 0:
            if lineage[0] == 'BaseEvent':
                availableFields.update(zip(DataModels.baseEventAttributes, DataModels.baseEventAttributes))
            # discard BaseObject
            lineage = DataModels.stripBaseObject(lineage, outputMode='list')
            # iterate through lineage
            # get attributes for each object
            for x in range(0, len(lineage)):
                # create lineage_part
                lineagePart = lineage[x]
                # get attribute lineage
                # note the x+1 here which does not overflow
                # >>> mylist = ['a', 'b', 'c', 'd', 'e']
                # >>> '.'.join(mylist[:5])
                # >>> 'a.b.c.d.e'
                attributeLineage = '.'.join(lineage[0:x + 1])
                # get attributes for this object
                attributes = DataModels.getObjectAttributes(lineagePart, modelJson)
                # add each attribute w/ it's lineage to the list of avail fields
                for attribute in attributes:
                    availableFields[attributeLineage + '.' + attribute] = attribute
        else:
            availableFields = None

        return availableFields

    @staticmethod
    def isModelMixed(modelJson):
        """ Return a boolean as to whether the model has a mix of baseObjects
        @param modelJson  - The datamodel JSON specification

        @return bool
        """
        baseParents = set()

        for object in modelJson.get('objects', []):
            parentName = object.get('parentName')

            if parentName in DataModels.baseObjects:
                baseParents.add(parentName)

        return len(baseParents) > 1
