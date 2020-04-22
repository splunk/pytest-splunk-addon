'use strict';

define(['jquery', 'underscore', 'backbone', 'collections/SplunkDsBase'], function ($, _, Backbone, SplunkDBaseCollection) {

  return SplunkDBaseCollection.extend({
    url: 'search/tags',
    initialize: function initialize() {
      SplunkDBaseCollection.prototype.initialize.apply(this, arguments);
    }
  });
});
