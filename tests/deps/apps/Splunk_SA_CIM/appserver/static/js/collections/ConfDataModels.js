'use strict';

define(['jquery', 'backbone', 'underscore', 'collections/SplunkDsBase', '../models/ConfDataModel'], function ($, Backbone, _, SplunkDBaseCollection, ConfDataModel) {
    return SplunkDBaseCollection.extend({
        url: 'data/models',
        model: ConfDataModel
    });
});
