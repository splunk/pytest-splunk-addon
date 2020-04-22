'use strict';

require.config({
  paths: {
    'Macro': '../app/Splunk_SA_CIM/js/models/Macro'
  }
});

define(function (require, exports, module) {
  var SplunkDsBaseCollection = require('collections/SplunkDsBase'),
      Model = require('Macro');

  return SplunkDsBaseCollection.extend({
    url: 'admin/macros',
    model: Model,
    initialize: function initialize() {
      SplunkDsBaseCollection.prototype.initialize.apply(this, arguments);
    }
  });
});
