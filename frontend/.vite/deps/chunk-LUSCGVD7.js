import {
  require_react
} from "./chunk-2CLD7BNN.js";
import {
  __toESM
} from "./chunk-WOOG5QLI.js";

// node_modules/@mui/utils/esm/useOnMount/useOnMount.js
var React = __toESM(require_react(), 1);
var EMPTY = [];
function useOnMount(fn) {
  React.useEffect(fn, EMPTY);
}

// node_modules/@mui/utils/esm/useLazyRef/useLazyRef.js
var React2 = __toESM(require_react(), 1);
var UNINITIALIZED = {};
function useLazyRef(init, initArg) {
  const ref = React2.useRef(UNINITIALIZED);
  if (ref.current === UNINITIALIZED) {
    ref.current = init(initArg);
  }
  return ref;
}

export {
  useLazyRef,
  useOnMount
};
//# sourceMappingURL=chunk-LUSCGVD7.js.map
