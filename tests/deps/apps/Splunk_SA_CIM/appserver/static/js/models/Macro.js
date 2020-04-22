'use strict';

define(['jquery', 'underscore', 'backbone', 'models/SplunkDBase'], function ($, _, Backbone, SplunkDBaseModel) {

  return SplunkDBaseModel.extend({
    url: 'admin/macros',
    initialize: function initialize() {
      SplunkDBaseModel.prototype.initialize.apply(this, arguments);
    }
  });
});
