'use strict';

function _toConsumableArray(arr) { if (Array.isArray(arr)) { for (var i = 0, arr2 = Array(arr.length); i < arr.length; i++) { arr2[i] = arr[i]; } return arr2; } else { return Array.from(arr); } }

/**
 * Copyright (C) 2019 Splunk Inc. All Rights Reserved.
 */

require.config({
    paths: {
        'Macros': '../app/Splunk_SA_CIM/js/collections/Macros',
        'CIMSetupView': '../app/Splunk_SA_CIM/js/views/CIMSetupView'
    }
});

require(['jquery', 'underscore', 'backbone', 'util/splunkd_utils', 'splunkjs/mvc', 'splunkjs/mvc/sharedmodels', 'models/SplunkDBase', 'collections/SplunkDsBase', 'collections/services/data/Indexes', 'Macros', '../app/Splunk_SA_CIM/js/collections/ConfDataModels', '../app/Splunk_SA_CIM/js/models/ConfDataModel', '../app/Splunk_SA_CIM/js/collections/Tags', 'CIMSetupView', 'splunk.util', 'bootstrap.tab', 'splunkjs/mvc/simplexml/ready!'], function ($, _, Backbone, splunkd_utils, mvc, SharedModel, SplunkDBase, SplunkDsBase, Indexes, Macros, ConfDataModels, ConfDataModel, Tags, CIMSetupView, splunkUtils) {
    function reltime_compare(a, b) {
        // empty string or 0: All time = max integer
        var re = /^-(\d+)(s|h|d|m|w|q|y)/,
            order = {
            s: 1 / 86400,
            h: 1 / 24,
            d: 1,
            w: 7,
            m: 30,
            q: 90,
            y: 365
        },
            am = a.match(re),
            bm = b.match(re),
            ascore = am ? am[1] * order[am[2]] : a === '0' || a.length === 0 ? Number.MAX_SAFE_INTEGER : 0,
            bscore = bm ? bm[1] * order[bm[2]] : b === '0' || b.length === 0 ? Number.MAX_SAFE_INTEGER : 0;
        return a === b ? 0 : ascore - bscore;
    }

    function accel_validation(attrs, options) {
        var re = /^(-\d+(s|seconds?|h|hours?|d|days?|mon|months?|y|yrs?|years?|w|weeks?|q|qtrs?|quarters?)|0)$/;
        var enabled = splunkUtils.normalizeBoolean(attrs.acceleration);
        var max_time = Number(attrs['acceleration.max_time'] || 0);
        var earliest_time = attrs['acceleration.earliest_time'] || '';
        var backfill_time = attrs['acceleration.backfill_time'] || earliest_time;
        var max_concurrent = Number(attrs['acceleration.max_concurrent'] || 0);
        var manualRebuild = splunkUtils.normalizeBoolean(attrs['acceleration.manual_rebuilds']);
        var errors = {};

        if (typeof enabled !== 'boolean') {
            errors.enabled = "Enabled should be boolean";
        }

        if (enabled) {
            if (earliest_time.length && !earliest_time.match(re)) {
                errors.earliest_time = "Invalid Summary Range";
            }
            if (backfill_time.length && !backfill_time.match(re)) {
                errors.backfill_time = "Invalid Backfill Range";
            }
            if (reltime_compare(backfill_time, earliest_time) > 0) {
                errors.backfill_time = "Backfill Range should be more recent than Summary Range";
            }
            if (isNaN(max_time) || parseInt(max_time) !== max_time) {
                errors.max_time = "max_time should be an integer";
            }
            if (isNaN(max_concurrent) || parseInt(max_concurrent) !== max_concurrent) {
                errors.max_concurrent = "max_concurrent should be an integer";
            }
            if (typeof manualRebuild !== 'boolean') {
                errors.manual_rebuilds = "manual_rebuilds should be boolean";
            }
        }

        return !_.isEmpty(errors) ? errors : null;
    }

    function hasCapability(capability) {
        var promise = $.Deferred();

        // Get all capabilities for the logged in user
        $.ajax({
            url: splunkUtils.make_url('/splunkd/__raw/services/authentication/current-context?output_mode=json'),
            type: 'GET',
            async: true,
            success: function success(result) {
                if (result !== undefined && result.isOk === false) {
                    promise.reject('Context could not be obtained: ' + result.message);
                } else if (result.entry.length != 1) {
                    promise.reject('Context could not be obtained - wrong number of results: ' + result.entry.length);
                } else {
                    var res = false;
                    if ($.inArray(capability, result.entry[0].content.capabilities) >= 0) {
                        res = true;
                    }
                    promise.resolve(res);
                }
            },
            error: function error(jqXHR) {
                promise.reject(jqXHR);
            }
        });

        return promise;
    }

    var dmmacros = new Macros();
    var indexes = new Indexes();
    var datamodels = new ConfDataModels();
    var tags = new Tags();

    var tagsArr = [];
    var indexesArr = [];

    var macrosDfd = $.Deferred();
    var indexesDfd = $.Deferred();
    var datamodelsDfd = $.Deferred();
    var tagsDfd = $.Deferred();

    hasCapability('accelerate_datamodel').then(function (capabilityExists) {
        if (capabilityExists) {
            dmmacros.fetch({
                data: {
                    search: $.param({
                        name: 'cim_*_indexes'
                    }),
                    count: -1
                },
                success: function success() {
                    macrosDfd.resolve();
                },
                error: function error(collection, resp) {
                    console.error(resp);
                    macrosDfd.reject();
                }
            });

            indexes.fetch({
                data: {
                    count: -1
                },
                success: function success(collection) {
                    collection.each(function (model) {
                        indexesArr.push(model.entry.get('name'));
                    });
                    indexesDfd.resolve();
                },
                error: function error() {
                    indexesDfd.reject();
                }
            });

            datamodels.fetch({
                data: {
                    count: -1
                },
                success: function success(collection) {
                    collection.each(function (model) {
                        model.entry.content.validate = accel_validation;
                    });
                    datamodelsDfd.resolve();
                },
                error: function error() {
                    datamodelsDfd.reject();
                }
            });

            tags.fetch({
                data: {
                    count: -1
                },
                success: function success(collection) {
                    collection.each(function (model) {
                        tagsArr.push(model.entry.get('name'));
                    });
                    tagsDfd.resolve();
                },
                error: function error() {
                    tagsDfd.reject();
                }
            });

            Promise.all([macrosDfd, indexesDfd, datamodelsDfd, tagsDfd]).then(function () {
                var accelerations = {};
                datamodels.each(function (model) {
                    var entry = model.entry;
                    return accelerations[entry.get('name')] = entry.content.toJSON();
                });

                var view = new CIMSetupView({
                    el: $("#cim_setup_container"),
                    datamodels: datamodels,
                    dmmacros: dmmacros,
                    tags: tagsArr,
                    indexes: indexesArr
                });

                view.on('save', function (macros) {
                    view.setPrimaryBtn(_('Saving').t(), true);

                    var indexPromises = _.map(macros, function (mainMacro) {
                        var model = dmmacros.find(function (dmMacro) {
                            return dmMacro.entry.get('name') === mainMacro.get('name');
                        });

                        if (model) {
                            var name = mainMacro.get('name');
                            var previous = mainMacro.get('indexesInit');
                            var changed = mainMacro.get('indexes');
                            var indexesArray = changed.split(',');

                            if (changed !== previous) {
                                var definition = indexesArray.map(function (indexStr) {
                                    return indexStr ? 'index=' + indexStr : '';
                                }).join(' OR ');

                                mainMacro.set('indexesInit', changed);
                                model.entry.content.set('definition', '(' + definition + ')');

                                return model.save({}, {
                                    success: function success() {
                                        view.showUpdateStatus(name, false);
                                    },
                                    error: function error(model, response, options) {
                                        console.error(response);
                                        view.showUpdateStatus(name, true);
                                    }
                                });
                            }

                            return true;
                        }
                    });

                    var accelPromises = datamodels.filter(function (model) {
                        var name = model.entry.get('name');
                        var acc = model.entry.content;
                        var errors = acc.validate(acc.attributes);
                        var previousAttrs = accelerations[name];
                        var newAttrs = acc.toJSON();
                        // clones for checking for changes below
                        var prevCheck = Object.assign({}, previousAttrs);
                        var newCheck = Object.assign({}, newAttrs);

                        if (errors) {
                            var attrs = _.chain(errors).map(function (val, key) {
                                return [key, previousAttrs[key]];
                            }).object().value();
                            acc.set(attrs, {
                                silent: true
                            });

                            return false;
                        }

                        // Before we check for changes, remove eai:appName and eai:userName
                        // b/c they get arbitrarily updated if saved
                        delete prevCheck['eai:appName'];
                        delete prevCheck['eai:userName'];
                        delete newCheck['eai:appName'];
                        delete newCheck['eai:userName'];

                        // Before we check for changes, normalize values for
                        // acceleration and acceleration.manual_rebuilds
                        prevCheck['acceleration'] = splunkUtils.normalizeBoolean(prevCheck['acceleration']);
                        prevCheck['acceleration.manual_rebuilds'] = splunkUtils.normalizeBoolean(prevCheck['acceleration.manual_rebuilds']);
                        newCheck['acceleration'] = splunkUtils.normalizeBoolean(newCheck['acceleration']);
                        newCheck['acceleration.manual_rebuilds'] = splunkUtils.normalizeBoolean(newCheck['acceleration.manual_rebuilds']);

                        if (!_.isEqual(prevCheck, newCheck)) {
                            // if there was a change, we must make sure previous attrs are updated
                            // so that erroneous saves won't take place for subsequent save button clicks
                            accelerations[name] = newAttrs;
                            return true;
                        }

                        return false;
                    }).map(function (model) {
                        var macroname = 'cim_' + model.entry.get('name') + '_indexes';
                        return model.save({}, {
                            success: function success() {
                                view.showUpdateStatus(macroname, false);
                            },
                            error: function error(m, response, options) {
                                console.error(response);
                                view.showUpdateStatus(macroname, true);
                            }
                        });
                    });

                    Promise.all([].concat(_toConsumableArray(indexPromises), _toConsumableArray(accelPromises))).then(function () {
                        view.setPrimaryBtn(_('Save').t(), false);
                    });
                });

                view.on('cancel', function () {
                    var app = SharedModel.get('app').get('app');
                    window.location = splunkUtils.make_url('/manager/' + app + '/apps/local');
                });

                view.render();
            }).catch(function (response) {
                $('#cim_setup_container').html(_('An error occurred fetching assets. Please try again.').t());
            });
        } else {
            $('#cim_setup_container').html(_('You do not have permission to access this page. Please contact your Splunk administrator.').t());
        }
    }, function (failedResp) {
        console.error(failedResp);
    });
});
