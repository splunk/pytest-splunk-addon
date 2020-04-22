'use strict';

define(['jquery', 'backbone', 'underscore', 'splunk.util', 'models/SplunkDBase'], function ($, Backbone, _, splunkUtils, SplunkDBaseModel) {
    return SplunkDBaseModel.extend({
        urlRoot: 'data/models'
    });
});
