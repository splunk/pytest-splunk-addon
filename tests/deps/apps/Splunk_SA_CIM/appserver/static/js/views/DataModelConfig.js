"use strict";

/*
 * Copyright (C) 2018 Splunk Inc. All Rights Reserved.
 */

define(["jquery", "underscore", "backbone", "module", "views/Base", "views/shared/controls/ControlGroup", 'views/shared/controls/TextControl', 'views/shared/controls/SyntheticSelectControl', '../commonControl/AddonMenuControl', '../util/Utils', "splunk.util"], function ($, _, Backbone, module, BaseView, ControlGroup, TextControl, SyntheticSelectControl, AddonMenuControl, Utils, splunkUtil) {

    var VERSION_LABEL = splunkUtil.getConfigValue('VERSION_LABEL');

    return BaseView.extend({
        //
        // options: model { macro, dmConfigModel }
        //
        initialize: function initialize() {
            BaseView.prototype.initialize.apply(this, arguments);

            this._initAcceleration();
            this._initIndexes();
            this._initTags();
            this.startListening();
        },

        _initAcceleration: function _initAcceleration() {
            var modelContent = this.model.dmConfigModel.entry.content;
            var acceleration = modelContent.get('acceleration');
            var enabled = splunkUtil.normalizeBoolean(acceleration);

            console.info(enabled);
            this.children.enabled = new ControlGroup({
                label: _("Accelerate").t(),
                required: false,
                controlType: 'SyntheticCheckbox',
                controlOptions: {
                    model: modelContent,
                    modelAttribute: 'acceleration',
                    value: true
                }
            });

            this.children.backfill_time = new AddonMenuControl({
                label: _("Backfill Range").t(),
                enabled: enabled,
                required: false,
                appendItems: [{
                    value: 'y',
                    alternateValues: ['yrs', 'years'],
                    label: _("Year").t()
                }, {
                    value: 'q',
                    alternateValues: ['qtrs', 'quarters'],
                    label: _("Quarter").t()
                }, {
                    value: 'mon',
                    alternateValues: ['months'],
                    label: _("Month").t()
                }, {
                    value: 'w',
                    alternateValues: ['weeks'],
                    label: _("Week").t()
                }, {
                    value: 'd',
                    alternateValues: ['days'],
                    label: _("Day").t()
                }, {
                    value: 'h',
                    alternateValues: ['hours'],
                    label: _("Hour").t()
                }, {
                    value: 's',
                    alternateValues: ['seconds'],
                    label: _("Second").t()
                }],
                model: modelContent,
                modelAttribute: 'acceleration.backfill_time',
                placeholder: _('e.g. -1').t()
            });

            this.children.earliest_time = new AddonMenuControl({
                label: _("Summary Range").t(),
                enabled: enabled,
                required: false,
                appendItems: [{
                    value: 'y',
                    alternateValues: ['yrs', 'years'],
                    label: _("Year").t()
                }, {
                    value: 'q',
                    alternateValues: ['qtrs', 'quarters'],
                    label: _("Quarter").t()
                }, {
                    value: 'mon',
                    alternateValues: ['months'],
                    label: _("Month").t()
                }, {
                    value: 'w',
                    alternateValues: ['weeks'],
                    label: _("Week").t()
                }, {
                    value: 'd',
                    alternateValues: ['days'],
                    label: _("Day").t()
                }, {
                    value: 'h',
                    alternateValues: ['hours'],
                    label: _("Hour").t()
                }, {
                    value: 's',
                    alternateValues: ['seconds'],
                    label: _("Second").t()
                }],
                model: modelContent,
                modelAttribute: 'acceleration.earliest_time',
                placeholder: _('e.g. -1').t()

            });

            this.children.max_time = new ControlGroup({
                label: _("Max Summarization Search Time").t(),
                required: false,
                controlType: 'Text',
                enabled: enabled,
                controlOptions: {
                    model: modelContent,
                    modelAttribute: 'acceleration.max_time'
                }
            });

            // poll_buckets_until_maxtime is only configurable in Splunk 6.6+
            if (Utils.versionCompare(VERSION_LABEL, '6.6', '>=')) {
                this.children.poll_buckets = new ControlGroup({
                    label: _("Accelerate until maximum time").t(),
                    required: false,
                    controlType: 'SyntheticCheckbox',
                    enabled: enabled,
                    controlOptions: {
                        model: modelContent,
                        modelAttribute: 'acceleration.poll_buckets_until_maxtime'
                    }
                });
            }

            this.children.max_concurrent = new ControlGroup({
                label: _("Max Concurrent Summarization Searches").t(),
                required: false,
                controlType: 'Text',
                enabled: enabled,
                controlOptions: {
                    model: modelContent,
                    modelAttribute: 'acceleration.max_concurrent'
                }
            });

            // After changing the endpoint, manual_rebuilds attribute comes
            // back in several bool forms... we need to standardize here
            var manualRebuild = splunkUtil.normalizeBoolean(modelContent.get('acceleration.manual_rebuilds'));
            modelContent.set('acceleration.manual_rebuilds', manualRebuild ? 1 : 0);

            this.children.manual_rebuilds = new ControlGroup({
                label: _("Manual rebuilds").t(),
                required: false,
                controlType: 'SyntheticCheckbox',
                enabled: enabled,
                controlOptions: {
                    model: modelContent,
                    modelAttribute: 'acceleration.manual_rebuilds',
                    value: true
                }
            });

            // schedule_priority is only configurable in Splunk 6.5+
            if (Utils.versionCompare(VERSION_LABEL, '6.5', '>=')) {
                this.children.schedule_priority = new ControlGroup({
                    label: _("Schedule priority").t(),
                    required: false,
                    controlType: 'SyntheticSelect',
                    enabled: enabled,
                    controlOptions: {
                        model: modelContent,
                        modelAttribute: 'acceleration.schedule_priority',
                        items: [{
                            value: 'default',
                            label: _("default").t()
                        }, {
                            value: 'higher',
                            label: _("higher").t()
                        }, {
                            value: 'highest',
                            label: _("highest").t()
                        }],
                        popdownOptions: {
                            attachDialogTo: 'body'
                        }
                    }
                });
            }
        },

        _initIndexes: function _initIndexes() {
            this.children.indexes_whitelist = new ControlGroup({
                label: _("Indexes whitelist").t(),
                required: false,
                controlType: 'MultiInput',
                controlOptions: {
                    model: this.model.macro,
                    modelAttribute: 'indexes',
                    autoCompleteFields: _.uniq(this.options.indexes),
                    placeholder: _('Using all indexes.').t()
                }
            });
        },

        _initTags: function _initTags() {
            // tags_whitelist is only configurable in Splunk 6.6.4+
            if (Utils.versionCompare(VERSION_LABEL, '6.6.4', '>=')) {
                this.children.tags_whitelist = new ControlGroup({
                    label: _("Tags whitelist").t(),
                    required: false,
                    controlType: 'MultiInput',
                    controlOptions: {
                        model: this.model.dmConfigModel.entry.content,
                        modelAttribute: 'tags_whitelist',
                        autoCompleteFields: _.uniq(this.options.tags)
                    }
                });
            }
        },

        startListening: function startListening() {
            if (this.model.dmConfigModel.entry.content) {
                var mapping = {
                    enabled: this.children.enabled,
                    backfill_time: this.children.backfill_time,
                    earliest_time: this.children.earliest_time,
                    max_time: this.children.max_time,
                    poll_buckets: this.children.poll_buckets,
                    max_concurrent: this.children.max_concurrent,
                    manual_rebuilds: this.children.manual_rebuilds,
                    schedule_priority: this.children.schedule_priority
                };

                var sub_controls = [this.children.backfill_time, this.children.earliest_time, this.children.max_time, this.children.poll_buckets, this.children.max_concurrent, this.children.manual_rebuilds, this.children.schedule_priority];

                this.listenTo(this.model.dmConfigModel.entry.content, 'change', function (model) {
                    var errors = model.validate(model.attributes);
                    _.each(mapping, function (control) {
                        if (control) {
                            control.error(false);
                            control.$el.find('.help-block').remove();
                        }
                    });

                    if (errors) {
                        _.each(errors, function (msg, attr) {
                            var control = mapping[attr];

                            if (control) {
                                control.error(true, msg);
                                control.setHelpText(msg);
                            }
                        });
                    }
                });

                this.listenTo(this.model.dmConfigModel.entry.content, 'change:acceleration', function (model, value) {
                    var enabled = splunkUtil.normalizeBoolean(value);

                    if (enabled) {
                        _.each(sub_controls, function (control) {
                            if (control) {
                                control.enable();
                            }
                        });
                    } else {
                        _.each(sub_controls, function (control) {
                            if (control) {
                                control.disable();
                            }
                        });
                    }
                });
            }
        },

        render: function render() {
            var _this = this;

            if (this.model.macro) {
                _.each(this.children, function (child) {
                    child.render().appendTo(_this.$el);
                });
                var edit_in_manager_url = splunkUtil.make_full_url("manager/Splunk_SA_CIM/admin/macros/" + encodeURIComponent(this.model.macro.attributes.name), { 'action': 'edit' });
                var edit_in_manager_link = _.template("\n                        <span class=\"help-block indexes-whitelist-help\">                            <a href=\"<%= edit_in_manager_url %>\" target=\"_blank\" title=\"<%- _(\"Edit in Splunk Settings\").t() %>\">                                <%- _(\"Edit in Splunk Settings\").t() %>                                &nbsp;                                <i class=\"icon-external\"></i>                            </a>\n                    ");
                $('.controls .control', this.children.indexes_whitelist.$el).append(edit_in_manager_link({ edit_in_manager_url: edit_in_manager_url }));
            } else {
                this.$el.html("<p>" + _("No datamodel found").t() + "</p>");
            }
            return this;
        }
    });
});
