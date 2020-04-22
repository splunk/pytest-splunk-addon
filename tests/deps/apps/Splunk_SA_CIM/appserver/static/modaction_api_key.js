'use strict';

/**
 * Copyright (C) 2018 Splunk Inc. All Rights Reserved.
 */

require.config({
    paths: {
        'ModactionApiKeyView': '../app/Splunk_SA_CIM/js/views/ModactionApiKeyView'
    }
});

require(['jquery', 'underscore', 'splunkjs/mvc', 'ModactionApiKeyView', 'splunkjs/mvc/simplexml/ready!'], function ($, _, mvc, ModactionApiKeyView) {

    var app = 'Splunk_SA_CIM';
    var realm = 'cam_queue';

    var view = new ModactionApiKeyView({
        el: $('#modaction_api_key_container')
    });

    var updateApiKey = function updateApiKey(key_name, api_key) {
        var url = '/en-US/splunkd/__raw/servicesNS/nobody/' + encodeURIComponent(app) + '/storage/passwords';
        data = {
            'name': key_name,
            'password': api_key,
            'realm': realm
        };
        return $.when(deleteApiKey(key_name, true)).always(function () {
            $.ajax({
                type: 'POST',
                url: url,
                data: data,
                success: function success() {
                    view.displayStatus('#53A051', 'Successfully updated API Key!');
                },
                error: function error() {
                    view.clearInputs();
                    view.displayStatus('#DC4E41', 'Failed to update API Key!');
                },
                complete: function complete() {
                    view.setBtnText('#btn-save', _('Save').t(), false);
                }
            });
        });
    };

    var saveApiKey = function saveApiKey(key_name, api_key) {
        var url = '/en-US/splunkd/__raw/servicesNS/nobody/' + encodeURIComponent(app) + '/storage/passwords';
        view.setBtnText('#btn-save', _('Saving').t(), true);
        view.hideStatus();
        data = {
            'name': key_name,
            'password': api_key,
            'realm': realm
        };

        return $.ajax({
            type: 'POST',
            url: url,
            data: data,
            success: function success() {
                view.setBtnText('#btn-save', _('Save').t(), false);
                view.displayStatus('#53A051', 'Successfully saved API Key!');
            },
            error: function error(response) {
                if (response.statusText === 'Conflict') {
                    updateApiKey(key_name, api_key);
                } else {
                    view.clearInputs();
                    view.setBtnText('#btn-save', _('Save').t(), false);
                    view.displayStatus('#DC4E41', 'Failed to save API Key!');
                }
            }
        });
    };

    var showApiKey = function showApiKey(key_name) {
        var url = '/en-US/splunkd/__raw/servicesNS/nobody/' + encodeURIComponent(app) + '/storage/passwords' + ('/' + encodeURIComponent(realm) + ':' + encodeURIComponent(key_name) + ':');
        view.setBtnText('#btn-show', _('Loading').t(), true);
        view.hideStatus();

        return $.ajax({
            type: 'GET',
            url: url,
            data: {
                'output_mode': 'json'
            },
            success: function success(response) {
                if (response === undefined || response.entry.length !== 1) {
                    view.clearInputs();
                    view.displayStatus('#DC4E41', 'Failed to retrieve API Key!');
                } else {
                    var password = response['entry'][0]['content']['clear_password'];
                    view.displayApiKey(password);
                    view.displayStatus('#53A051', 'Successfully retrieved API Key!');
                }
            },
            error: function error() {
                view.clearInputs();
                view.displayStatus('#DC4E41', 'Failed to retrieve API Key!');
            },
            complete: function complete() {
                view.setBtnText('#btn-show', _('Show').t(), false);
            }
        });
    };

    var deleteApiKey = function deleteApiKey(key_name) {
        var update = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;

        var url = '/en-US/splunkd/__raw/servicesNS/nobody/' + encodeURIComponent(app) + '/storage/passwords' + ('/' + encodeURIComponent(realm) + ':' + encodeURIComponent(key_name) + ':');
        if (!update) view.setBtnText('#btn-delete', _('Deleting').t(), true);
        view.hideStatus();

        return $.ajax({
            type: 'DELETE',
            url: url,
            success: function success() {
                if (!update) view.clearInputs();
                view.displayStatus('#53A051', 'Successfully deleted API Key!');
            },
            error: function error() {
                view.clearInputs();
                if (!update) view.displayStatus('#DC4E41', 'Failed to delete API Key!');
            },
            complete: function complete() {
                if (!update) view.setBtnText('#btn-delete', _('Delete').t(), false);
            }
        });
    };

    view.on('save', function (key_name, api_key) {
        saveApiKey(key_name, api_key);
    });

    view.on('show', function (key_name) {
        showApiKey(key_name);
    });

    view.on('delete', function (key_name) {
        deleteApiKey(key_name);
    });

    view.render();
});
