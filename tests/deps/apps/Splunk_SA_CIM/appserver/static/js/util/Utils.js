'use strict';

define(function () {
    var Utils = {
        versionGreaterThan: function versionGreaterThan(v1, v2) {
            var result = false;
            for (i in v1) {
                if (v1[i] > v2[i]) {
                    result = true;
                    break;
                }
                if (v1[i] < v2[i]) {
                    result = false;
                    break;
                }
            }

            return result;
        },
        versionLessThan: function versionLessThan(v1, v2) {
            var result = false;
            for (i in v1) {
                if (v1[i] < v2[i]) {
                    result = true;
                    break;
                }
                if (v1[i] > v2[i]) {
                    result = false;
                    break;
                }
            }

            return result;
        },
        versionCompare: function versionCompare(version1, version2, comparator) {
            var v1Split = version1.split('.');
            var v2Split = version2.split('.');

            // Fill the other array with 0 if no value exists
            while (v1Split.length < v2Split.length) {
                v1Split.push('0');
            }while (v2Split.length < v1Split.length) {
                v2Split.push('0');
            }switch (comparator) {
                case '>':
                    return Utils.versionGreaterThan(v1Split, v2Split);
                case '>=':
                    return Utils.versionGreaterThan(v1Split, v2Split) || version1 === version2;
                case '<':
                    return Utils.versionLessThan(v1Split, v2Split);
                case '<=':
                    return Utils.versionLessThan(v1Split, v2Split) || version1 === version2;
                default:
                    // is equal to
                    return version1 === version2;
            }
        }
    };

    return Utils;
});
