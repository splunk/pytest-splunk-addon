'use strict';

/*
 * Copyright (C) 2015 Splunk Inc. All Rights Reserved.
 */

define(['underscore', 'backbone', 'jquery', 'util/splunkd_utils', 'views/Base', 'views/shared/controls/TextControl', '../app/Splunk_SA_CIM/js/views/DataModelConfig', 'splunk.util'], function (_, Backbone, $, splunkd_utils, BaseView, TextControl, DataModelConfig, splunkUtil) {

    var BREADCRUMB = '\n            <div class="breadcrumb">\n                <span><a href="<%- url %>"><%- text %></a> &raquo; Splunk_SA_CIM</span>\n            </div>';

    return BaseView.extend({
        _macroTemplate: _.template('\n                <div data-macroname="<%- name %>" class="datamodel_item">\n                    <div class="datamodel_name">\n                        <span><%- label %></span>\n                        <span class="hide alert alert-info">\n                            <i class="icon icon-alert"></i><%- _("Saved").t() %>\n                        </span>\n                        <span class="hide alert alert-error">\n                            <i class="icon icon-alert"></i><%- _("Save failed").t() %>\n                        </span>\n                    </div>\n                    <div class="indexes_list"></div>\n                 </div>\n            '),

        template: '\n                <div class="cimSetupWrapper">\n                    <div class="header">\n                        <h2><%- _("Splunk Common Information Model Add-on Set Up").t() %></h2>\n                        <div>\n                            <%- _("Modify data model settings to constrain data model searches to specific indexes, set a backfill time, and more.").t() %><br>\n                            <a href="<%- Splunk.util.make_url(\'/app/Splunk_SA_CIM/modaction_api_key\') %>" target="_blank" title="<%- _("Modaction API Key").t() %>">\n                                <%- _("Manage API Key").t() %>\n                                <i class="icon-external"></i>\n                            </a>\n                        </div>\n                    </div>\n                    <div class="layoutBodyColumns layoutRow addDataBody" style="position: relative">\n                        <div class="layoutCol layoutColLeft scroll-y">\n                            <div class="datamodel_head"><%- _("Data Models").t() %></div>\n                            <div class="datamodel_list"></div>\n                        </div>\n                        <div class="layoutCol layoutColRight scroll-y">\n                            <div class="datamodel_config"></div>\n                            <div id="settings" class="tab-pane fade in active">\n                                <h3><%- _("Settings").t() %></h3>\n                                <span class="help-block">\n                                    <%- _("Acceleration properties for the selected data model.").t() %>\n                                    <a href="<%- Splunk.util.make_full_url(\'/help\', {location: \'cim_datamodel_acceleration_setup\'}) %>" target="_blank" title="<%- _("Splunk help").t() %>">\n                                        <%- _("Learn more").t() %>\n                                        &nbsp;\n                                        <i class="icon-external"></i>\n                                    </a>\n                                </span>\n                                <div class="settingsForm form-horizontal" />\n                            </div>\n                        </div>\n                    </div>\n                    <div class="modal-footer">\n                        <a href="#" class="btn cancel modal-btn-cancel pull-left" data-dismiss="modal">\n                            <%- _("Cancel").t() %>\n                        </a>\n                        <a href="#" class="btn btn-primary modal-btn-primary pull-right">\n                            <%- _("Save").t() %>\n                        </a>\n                    </div>\n                </div>\n            ',

        events: {
            'click .more': 'expandMacroInfo',
            'click .datamodel_item': 'selectMacro',
            'click .btn-primary': 'save',
            'click .btn.cancel': 'cancel'
        },

        initialize: function initialize() {
            var _this = this;

            BaseView.prototype.initialize.apply(this, arguments);

            this.datamodels = this.options.datamodels;
            this.dmmacros = this.options.dmmacros;
            this.indexes = this.options.indexes;
            this.tags = this.options.tags;
            this.macros = {};

            if (!this.options.max_display_count) {
                this.options.max_display_count = 70;
            }

            var macros = this.dmmacros,
                reg = 'index\\s*=\\s*([\\w-*]+|"[\\w-*]+")',
                reall = new RegExp(reg, 'g'),
                reone = new RegExp(reg),
                allidx = _.pluck(this.indexes, 'name');

            macros.each(function (macroModel, index) {
                var name = macroModel.entry.get('name');
                var modelName = name.slice(4, -8);
                var definition = macroModel.entry.content.get('definition');
                var idxmatch = definition.match(reall);
                var indexes = [];
                var indexesStrList = '';

                if (idxmatch) {
                    indexes = _.chain(idxmatch).map(function (idxstr) {
                        var value = idxstr.match(reone)[1],
                            len = value.length;

                        if (value[0] === '"' && value[len - 1] === '"') {
                            value = value.substring(1, len - 1);
                        }

                        return value;
                    }).value();
                    indexesStrList = indexes.join(',');
                }

                var newMacroModel = new Backbone.Model();
                var macroData = {
                    name: name,
                    modelName: modelName,
                    indexes: indexesStrList,
                    indexesInit: indexesStrList
                };
                newMacroModel.set(macroData);
                _this.listenTo(newMacroModel, 'change:indexes', function () {
                    var selector = '.datamodel_item[data-macroname="' + name + '"]';
                    var div = _this.$(selector);
                    _this.setMacroInfo(div, newMacroModel, _this.options.max_display_count);
                });

                _this.macros[name] = newMacroModel;

                if (index === 0) {
                    _this.active_macro = name;
                }
            }, this);

            var dmConfigModel = this.datamodels.findByEntryName(this.macros[this.active_macro].get('modelName'));
            this.children.datamodel_config = new DataModelConfig({
                model: {
                    macro: this.macros[this.active_macro],
                    dmConfigModel: dmConfigModel
                },
                tags: this.tags,
                indexes: this.indexes
            });
        },

        selectMacro: function selectMacro(e) {
            e.preventDefault();
            var item = $(e.target).closest('.datamodel_item');
            var macroname = item.data('macroname');
            var macro = this.macros[macroname];

            this.$('.datamodel_item.selected').removeClass('selected');
            item.addClass('selected');
            this.active_macro = macroname;

            if (this.children.datamodel_config) {
                this.children.datamodel_config.remove();
            }

            var dmConfigModel = this.datamodels.findByEntryName(this.macros[this.active_macro].get('modelName'));
            this.children.datamodel_config = new DataModelConfig({
                model: {
                    macro: macro,
                    dmConfigModel: dmConfigModel
                },
                tags: this.tags,
                indexes: this.indexes
            });

            this.children.datamodel_config.render().appendTo(this.$('.settingsForm.form-horizontal'));
        },

        expandMacroInfo: function expandMacroInfo(e) {
            e.preventDefault();
            var target = $(e.target).closest('.datamodel_item'),
                macroname = target.data('macroname'),
                macro = this.macros[macroname];

            if (macro) {
                this.setMacroInfo(target, macro);
            }

            e.stopImmediatePropagation();
        },

        setMacroInfo: function setMacroInfo(div, macro, maxDisplayCount) {
            var el = div.find('.indexes_list');
            var indexes = macro.get('indexes');
            var max = maxDisplayCount || 1000;
            var restrictions = '';
            var idxshow = [];

            if (indexes) {
                restrictions = splunkUtil.sprintf(_('Restricted to: %s').t(), indexes);
            } else {
                restrictions = _('No restriction').t();
            }

            el.html(restrictions);

            if (indexes.length > max) {
                var more = $('<span class="more">' + _("show all").t() + '</span>');

                el.append(more);
            }
        },

        showUpdateStatus: function showUpdateStatus(macroname, error) {
            var div = this.$('.datamodel_item[data-macroname="' + macroname + '"]'),
                alerterr = div.find('span.alert.alert-error'),
                alertinfo = div.find('span.alert.alert-info');

            if (error) {
                alerterr.removeClass("hide");
                alertinfo.addClass("hide");
            } else {
                alertinfo.removeClass("hide");
                alerterr.addClass("hide");
                setTimeout(function () {
                    alertinfo.addClass("hide");
                }, 5000);
            }
        },

        renderMacroList: function renderMacroList() {
            var _this2 = this;

            var maxDisplayCount = this.options.max_display_count;
            var selectedMacro = this.macros[this.active_macro];
            var listDiv = this.$('.datamodel_list');

            _.each(this.macros, function (macro) {
                // 'model.modelName' is of the form 'BLAH_BLAH'
                // 'label' needs to be 'BLAH BLAH'
                var _label = macro.get('modelName').replace(/_/g, " ");

                // 'label' needs to be translated
                _label = _(_label).t();

                var entry = $(_this2._macroTemplate({
                    name: macro.get('name'),
                    label: _label
                }));

                _this2.setMacroInfo(entry, macro, maxDisplayCount);

                if (macro.get('name') === selectedMacro.get('name')) {
                    entry.addClass('selected');
                }

                listDiv.append(entry);
            });
        },

        save: function save(e) {
            e.preventDefault();
            this.trigger('save', this.macros);
        },

        cancel: function cancel(e) {
            e.preventDefault();
            this.trigger('cancel');
        },

        setPrimaryBtn: function setPrimaryBtn(text, disabled) {
            var btn = this.$('.btn-primary');
            if (_.isString(text)) {
                btn.text(text);
            }

            if (disabled === true) {
                btn.addClass('nopointer');
            } else {
                btn.removeClass('nopointer');
            }
        },

        render: function render() {
            var breadcrumb = $(_.template(BREADCRUMB, {
                url: splunkUtil.make_url('manager/Splunk_SA_CIM/apps/local'),
                text: _("Apps").t()
            }));

            this.$el.html(this.compiledTemplate());
            this.renderMacroList();
            this.children.datamodel_config.render().appendTo(this.$('.settingsForm.form-horizontal'));

            $('.dashboard-header').append(breadcrumb);

            return this;
        }
    });
});
