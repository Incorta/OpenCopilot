"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var _default = function _default(_ref) {
  var palette = _ref.palette,
      spacing = _ref.spacing;
  var radius = spacing(2.5);
  var size = spacing(4);
  var rightBgColor = palette.primary.main; // if you want the same as facebook messenger, use this color '#09f'

  return {
    avatar: {
      width: size,
      height: size
    },
    rowContainer: {
        paddingTop: 10,
        paddingBottom: 10
    },
    leftRow: {
      textAlign: 'left',
    },
    rightRow: {
      textAlign: 'right',
    },
    msg: {
      padding: spacing(1, 2),
      borderRadius: 4,
      marginBottom: 4,
      display: 'inline-block',
      wordBreak: 'break-word',
      fontFamily: // eslint-disable-next-line max-len
      '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol"',
      fontSize: '14px'
    },
    left: {
      borderTopRightRadius: radius,
      borderBottomRightRadius: radius,
      backgroundColor: 'white'
    },
    right: {
      borderTopLeftRadius: radius,
      borderBottomLeftRadius: radius,
      backgroundColor: rightBgColor,
      color: palette.common.white
    },
    leftFirst: {
      borderTopLeftRadius: radius
    },
    leftLast: {
      borderBottomLeftRadius: radius
    },
    rightFirst: {
      borderTopRightRadius: radius
    },
    rightLast: {
      borderBottomRightRadius: radius
    }
  };
};

exports["default"] = _default;