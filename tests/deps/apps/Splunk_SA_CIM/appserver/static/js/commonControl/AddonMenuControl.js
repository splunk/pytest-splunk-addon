'use strict';

define(['underscore', 'views/Base', 'views/shared/controls/Control', 'views/shared/controls/TextControl', 'views/shared/controls/SyntheticSelectControl', 'module'], function (_, BaseView, Control, TextControl, SyntheticSelectControl, module) {

    /**
     * Control to add append menu along with a text box
     *
     * @param {Object} options
     *       {Object} model - The model to operate on
     *       {string} modelAttribute - The attribute of the model that will be changed
     *       {string} label - The label to identify the input-append
     *       {boolean} required - If the value for this input is required
     *       {boolean} enabled - Notifies if the control chould be enabled/disabled
     *       {Object} appendItems - An array of elements to be populated in the appendMenu with following options
     *                             ~ value - the value for this items
     *                             ~ label - the label that will show with the items
     *                             ~alternateValues - an array of other possible values for this item
     */

    return Control.extend({
        moduleId: module.id,

        initialize: function initialize(options) {
            Control.prototype.initialize.call(this, options);
            options = options || {};
            this.$el.addClass(options.className);

            this.options.appendItems.push({
                value: '',
                label: _("N/A").t()
            });
            this.children.appendMenu = new SyntheticSelectControl({
                items: this.options.appendItems,
                className: 'timepicker-control-menu input-append',
                toggleClassName: 'btn',
                menuWidth: 'narrow'
            });
            this.children.textNum = new TextControl({
                modelAttribute: this.options.modelAttribute,
                enabled: this.options.enabled,
                className: 'input-append input-prepend',
                placeholder: this.options.placeholder
            });

            this.children.textNum.on('change', this.handleControlValueChange, this);
            this.children.appendMenu.on('change', this.handleControlValueChange, this);

            this._createRegexForSetValue(this.options.appendItems);

            if (this.model.get(this.options.modelAttribute) !== undefined) {
                var controlValue = this.model.get(this.options.modelAttribute).match(this.setRegex);
                if (controlValue != null) {
                    this.applyValueToChildren(controlValue[1], controlValue[2]);
                }
            }
        },

        handleControlValueChange: function handleControlValueChange() {
            this.setValue(this.getValue(), false);
        },

        applyValueToChildren: function applyValueToChildren(textValue, appendValue) {
            // Subclasses should implement
            this.children.textNum.setValue(textValue);
            this.children.appendMenu.setValue(appendValue);
        },

        getValue: function getValue() {
            return '' + this.children.textNum.getValue() + this.children.appendMenu.getValue();
        },

        render: function render() {
            if (!this.el.innerHTML) {
                var html = _(this.template).template({});
                this.$el.html(html);
                this.$('.number-text-container').append(this.children.textNum.render().el);
                this.$('.append-menu-container').append(this.children.appendMenu.render().el);
                this.$('.timepicker-label').html(this.options.label);

                if (!this.options.enabled) {
                    this.disable();
                }
            }

            return this;
        },

        enable: function enable() {
            this.children.textNum.enable();
            this.children.appendMenu.enable();
        },

        disable: function disable() {
            this.children.textNum.disable();
            this.children.appendMenu.disable();
        },

        //build a regex to match the value with the append menu
        _createRegexForSetValue: function _createRegexForSetValue(appendItems) {
            var regexString = '';
            regexString = '(-?\\d+)(' + this._createRegexforItems(appendItems) + ')*';
            this.setRegex = new RegExp(regexString);
        },

        //build regex for each menu items array
        _createRegexforItems: function _createRegexforItems(itemsArray) {
            var _this = this;

            var regexString = '';
            _.each(itemsArray, function (item, index) {

                var val = _this.replaceSpecialChars(item.value);
                regexString = regexString + val + '|';

                if (item.alternateValues) {
                    var seg = _this.buildRegexSegment(item.alternateValues);
                    regexString = regexString + seg;
                }

                if (index < itemsArray.length - 1) {
                    regexString = regexString + '|';
                }
            });

            return regexString;
        },

        //build regex for alternate values for each menu item
        buildRegexSegment: function buildRegexSegment(valueArray) {
            var _this2 = this;

            var regexString = '';
            _.each(valueArray, function (item, index) {

                var val = _this2.replaceSpecialChars(item);
                regexString = regexString + val;
                if (index < valueArray.length - 1) {
                    regexString = regexString + '|';
                }
            });
            return regexString;
        },

        replaceSpecialChars: function replaceSpecialChars(str) {
            //The values of strings could be special characters which need to be escaped in the regex string
            return str.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
        },

        error: function error(flag, msg) {
            this.options.error = flag;
            if (flag) {
                this.$el.addClass('error');
                this.children.textNum.$el.find('input').css('color', '#d6563c');
                this.children.textNum.$el.find('input').css('border-color', '#d6563c');
            } else {
                this.$el.removeClass('error');
                this.children.textNum.$el.find('input').css('color', '');
                this.children.textNum.$el.find('input').css('border-color', '');
            }
        },

        // NOTE: The help text is intentionally not HTML-escaped, it is up to the caller to
        // pre-process this input as need to avoid XSS attacks.
        setHelpText: function setHelpText(msg) {
            this.$el.append('<span class="help-block" style="margin-left: 180px; margin-bottom: 8px;">' + msg + '</span>');
            if (this.options.error) {
                this.$el.find('.help-block').css('color', '#d6563c');
            }
        },

        template: '\n        <div class="timepicker-control" style="display: inline-flex;margin-bottom: 10px;">\n          <label class="control-label timepicker-label"></label>\n          <div class="number-text-container" style="float: left;margin-left: 20px;"></div>\n          <div class="append-menu-container"></div>\n        </div>\n        '
    });
});
