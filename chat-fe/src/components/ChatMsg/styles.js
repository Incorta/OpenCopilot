"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
Object.defineProperty(exports, "defaultChatMsgStyles", {
  enumerable: true,
  get: function get() {
    return _defaultChatMsg["default"];
  }
});
Object.defineProperty(exports, "default", {
  enumerable: true,
  get: function get() {
    return _defaultChatMsg["default"];
  }
});
exports.useDefaultChatMsgStyles = void 0;

var _makeStyles = _interopRequireDefault(require("@material-ui/core/styles/makeStyles"));

var _defaultChatMsg = _interopRequireDefault(require("./defaultChatMsg.styles"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }

var useDefaultChatMsgStyles = (0, _makeStyles["default"])(_defaultChatMsg["default"]);
exports.useDefaultChatMsgStyles = useDefaultChatMsgStyles;