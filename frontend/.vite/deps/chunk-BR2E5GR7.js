import {
  useLazyRef,
  useOnMount
} from "./chunk-LUSCGVD7.js";
import {
  chainPropTypes
} from "./chunk-JX37XSKT.js";
import {
  require_prop_types
} from "./chunk-EJ34WKIJ.js";
import {
  __publicField,
  __toESM
} from "./chunk-WOOG5QLI.js";

// node_modules/@mui/utils/esm/useTimeout/useTimeout.js
var Timeout = class _Timeout {
  constructor() {
    __publicField(this, "currentId", null);
    __publicField(this, "clear", () => {
      if (this.currentId !== null) {
        clearTimeout(this.currentId);
        this.currentId = null;
      }
    });
    __publicField(this, "disposeEffect", () => {
      return this.clear;
    });
  }
  static create() {
    return new _Timeout();
  }
  /**
   * Executes `fn` after `delay`, clearing any previously scheduled call.
   */
  start(delay, fn) {
    this.clear();
    this.currentId = setTimeout(() => {
      this.currentId = null;
      fn();
    }, delay);
  }
};
function useTimeout() {
  const timeout = useLazyRef(Timeout.create).current;
  useOnMount(timeout.disposeEffect);
  return timeout;
}

// node_modules/@mui/utils/esm/elementTypeAcceptingRef/elementTypeAcceptingRef.js
var import_prop_types = __toESM(require_prop_types(), 1);
function isClassComponent(elementType) {
  const {
    prototype = {}
  } = elementType;
  return Boolean(prototype.isReactComponent);
}
function elementTypeAcceptingRef(props, propName, componentName, location, propFullName) {
  const propValue = props[propName];
  const safePropName = propFullName || propName;
  if (propValue == null || // When server-side rendering React doesn't warn either.
  // This is not an accurate check for SSR.
  // This is only in place for emotion compat.
  // TODO: Revisit once https://github.com/facebook/react/issues/20047 is resolved.
  typeof window === "undefined") {
    return null;
  }
  let warningHint;
  if (typeof propValue === "function" && !isClassComponent(propValue)) {
    warningHint = "Did you accidentally provide a plain function component instead?";
  }
  if (warningHint !== void 0) {
    return new Error(`Invalid ${location} \`${safePropName}\` supplied to \`${componentName}\`. Expected an element type that can hold a ref. ${warningHint} For more information see https://mui.com/r/caveat-with-refs-guide`);
  }
  return null;
}
var elementTypeAcceptingRef_default = chainPropTypes(import_prop_types.default.elementType, elementTypeAcceptingRef);

// node_modules/@mui/utils/esm/refType/refType.js
var import_prop_types2 = __toESM(require_prop_types(), 1);
var refType = import_prop_types2.default.oneOfType([import_prop_types2.default.func, import_prop_types2.default.object]);
var refType_default = refType;

export {
  Timeout,
  useTimeout,
  elementTypeAcceptingRef_default,
  refType_default
};
//# sourceMappingURL=chunk-BR2E5GR7.js.map
