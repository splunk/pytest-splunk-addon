'use strict';

/*
 * Copyright (C) 2018 Splunk Inc. All Rights Reserved.
 */

define(['underscore', 'jquery', 'util/splunkd_utils', 'views/Base', 'splunk.util'], function (_, $, splunkd_utils, BaseView, splunkUtil) {
    var BREADCRUMB = '\n            <div class="breadcrumb">\n                <span><a href="<%- url %>"><%- text %></a> &raquo; Splunk_SA_CIM</span>\n            </div>';

    return BaseView.extend({

        template: '\n                <div class="form-board">\n                    <%- _("Key Name").t() %>:<br>\n                    <input type="text" id="key_name"><br>\n                    <%- _("API Key").t() %>:<br>\n                    <input type="text" id="api_key"><br>\n                    <div id="buttons">\n                        <a href="#" class="btn btn-primary btn-save">\n                            <%- _("Save").t() %>\n                        </a>\n                        <a href="#" class="btn btn-primary btn-show">\n                            <%- _("Show").t() %>\n                        </a>\n                        <a href="#" class="btn btn-danger btn-delete">\n                            <%- _("Delete").t() %>\n                        </a>\n                    </div>\n                    <div id="status"></div>\n                </div>\n            ',

        events: {
            'click .btn-save': 'save',
            'click .btn-delete': 'delete',
            'click .btn-show': 'show'
        },

        initialize: function initialize() {
            BaseView.prototype.initialize.apply(this, arguments);
        },

        save: function save(e) {
            e.preventDefault();
            this.trigger('save', this.$('#key_name').val(), this.$('#api_key').val());
        },

        delete: function _delete(e) {
            e.preventDefault();
            this.trigger('delete', this.$('#key_name').val());
        },

        show: function show(e) {
            e.preventDefault();
            this.trigger('show', this.$('#key_name').val());
        },

        setBtnText: function setBtnText(btnToSet, text, disabled) {
            var btn = this.$(btnToSet);
            if (_.isString(text)) {
                btn.text(text);
            }

            if (disabled === true) {
                btn.addClass('nopointer');
            } else {
                btn.removeClass('nopointer');
            }
        },

        displayApiKey: function displayApiKey(password) {
            this.$('#api_key').val(password);
        },

        clearInputs: function clearInputs() {
            this.$('input').val('');
        },

        hideStatus: function hideStatus() {
            this.$('#status').css('display', 'none');
        },

        displayStatus: function displayStatus(color, status) {
            this.$('#status').css('display', 'block');
            this.$('#status').css('color', color);
            this.$('#status').text(status);
        },

        render: function render() {
            var breadcrumb = $(_.template(BREADCRUMB, {
                url: splunkUtil.make_url('manager/Splunk_SA_CIM/apps/local'),
                text: _("Apps").t()
            }));

            this.$el.html(this.compiledTemplate());
            $('.dashboard-header').append(breadcrumb);
            return this;
        }
    });
});
