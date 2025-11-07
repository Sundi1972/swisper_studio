import {
  createSelectorCreator,
  lruMemoize,
  require_shim
} from "./chunk-ZAR7M645.js";
import {
  useLazyRef,
  useOnMount
} from "./chunk-LUSCGVD7.js";
import {
  useThemeProps
} from "./chunk-FSGOIAKX.js";
import {
  _extends
} from "./chunk-HQ6ZTAWL.js";
import {
  require_jsx_runtime
} from "./chunk-X3VLT5EQ.js";
import {
  require_react
} from "./chunk-2CLD7BNN.js";
import {
  __commonJS,
  __publicField,
  __toESM
} from "./chunk-WOOG5QLI.js";

// node_modules/use-sync-external-store/cjs/use-sync-external-store-shim/with-selector.development.js
var require_with_selector_development = __commonJS({
  "node_modules/use-sync-external-store/cjs/use-sync-external-store-shim/with-selector.development.js"(exports) {
    "use strict";
    (function() {
      function is(x, y) {
        return x === y && (0 !== x || 1 / x === 1 / y) || x !== x && y !== y;
      }
      "undefined" !== typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ && "function" === typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStart && __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStart(Error());
      var React13 = require_react(), shim = require_shim(), objectIs = "function" === typeof Object.is ? Object.is : is, useSyncExternalStore = shim.useSyncExternalStore, useRef4 = React13.useRef, useEffect4 = React13.useEffect, useMemo3 = React13.useMemo, useDebugValue = React13.useDebugValue;
      exports.useSyncExternalStoreWithSelector = function(subscribe, getSnapshot, getServerSnapshot, selector, isEqual) {
        var instRef = useRef4(null);
        if (null === instRef.current) {
          var inst = { hasValue: false, value: null };
          instRef.current = inst;
        } else inst = instRef.current;
        instRef = useMemo3(
          function() {
            function memoizedSelector(nextSnapshot) {
              if (!hasMemo) {
                hasMemo = true;
                memoizedSnapshot = nextSnapshot;
                nextSnapshot = selector(nextSnapshot);
                if (void 0 !== isEqual && inst.hasValue) {
                  var currentSelection = inst.value;
                  if (isEqual(currentSelection, nextSnapshot))
                    return memoizedSelection = currentSelection;
                }
                return memoizedSelection = nextSnapshot;
              }
              currentSelection = memoizedSelection;
              if (objectIs(memoizedSnapshot, nextSnapshot))
                return currentSelection;
              var nextSelection = selector(nextSnapshot);
              if (void 0 !== isEqual && isEqual(currentSelection, nextSelection))
                return memoizedSnapshot = nextSnapshot, currentSelection;
              memoizedSnapshot = nextSnapshot;
              return memoizedSelection = nextSelection;
            }
            var hasMemo = false, memoizedSnapshot, memoizedSelection, maybeGetServerSnapshot = void 0 === getServerSnapshot ? null : getServerSnapshot;
            return [
              function() {
                return memoizedSelector(getSnapshot());
              },
              null === maybeGetServerSnapshot ? void 0 : function() {
                return memoizedSelector(maybeGetServerSnapshot());
              }
            ];
          },
          [getSnapshot, getServerSnapshot, selector, isEqual]
        );
        var value = useSyncExternalStore(subscribe, instRef[0], instRef[1]);
        useEffect4(
          function() {
            inst.hasValue = true;
            inst.value = value;
          },
          [value]
        );
        useDebugValue(value);
        return value;
      };
      "undefined" !== typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ && "function" === typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStop && __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStop(Error());
    })();
  }
});

// node_modules/use-sync-external-store/shim/with-selector.js
var require_with_selector = __commonJS({
  "node_modules/use-sync-external-store/shim/with-selector.js"(exports, module) {
    "use strict";
    if (false) {
      module.exports = null;
    } else {
      module.exports = require_with_selector_development();
    }
  }
});

// node_modules/@mui/x-tree-view/node_modules/@mui/x-internals/esm/warning/warning.js
var warnedOnceCache = /* @__PURE__ */ new Set();
function warnOnce(message, gravity = "warning") {
  if (false) {
    return;
  }
  const cleanMessage = Array.isArray(message) ? message.join("\n") : message;
  if (!warnedOnceCache.has(cleanMessage)) {
    warnedOnceCache.add(cleanMessage);
    if (gravity === "error") {
      console.error(cleanMessage);
    } else {
      console.warn(cleanMessage);
    }
  }
}

// node_modules/@mui/x-tree-view/esm/internals/zero-styled/index.js
function createUseThemeProps(name) {
  return useThemeProps;
}

// node_modules/@mui/x-tree-view/esm/internals/TreeViewProvider/TreeViewStyleContext.js
var React = __toESM(require_react(), 1);
var TreeViewStyleContext = React.createContext({
  classes: {},
  slots: {},
  slotProps: {}
});
if (true) TreeViewStyleContext.displayName = "TreeViewStyleContext";
var useTreeViewStyleContext = () => {
  return React.useContext(TreeViewStyleContext);
};

// node_modules/@mui/x-tree-view/esm/internals/TreeViewProvider/TreeViewProvider.js
var React3 = __toESM(require_react(), 1);

// node_modules/@mui/x-tree-view/esm/internals/TreeViewProvider/TreeViewContext.js
var React2 = __toESM(require_react(), 1);
var TreeViewContext = React2.createContext(null);
if (true) TreeViewContext.displayName = "TreeViewContext";
var useTreeViewContext = () => {
  const context = React2.useContext(TreeViewContext);
  if (context == null) {
    throw new Error(["MUI X: Could not find the Tree View context.", "It looks like you rendered your component outside of a SimpleTreeView or RichTreeView parent component.", "This can also happen if you are bundling multiple versions of the Tree View."].join("\n"));
  }
  return context;
};

// node_modules/@mui/x-tree-view/esm/internals/TreeViewProvider/TreeViewProvider.js
var import_jsx_runtime = __toESM(require_jsx_runtime(), 1);
var EMPTY_OBJECT = {};
function TreeViewProvider(props) {
  const {
    contextValue,
    classes = EMPTY_OBJECT,
    slots = EMPTY_OBJECT,
    slotProps = EMPTY_OBJECT,
    children
  } = props;
  const styleContextValue = React3.useMemo(() => ({
    classes,
    slots: {
      collapseIcon: slots.collapseIcon,
      expandIcon: slots.expandIcon,
      endIcon: slots.endIcon
    },
    slotProps: {
      collapseIcon: slotProps.collapseIcon,
      expandIcon: slotProps.expandIcon,
      endIcon: slotProps.endIcon
    }
  }), [classes, slots.collapseIcon, slots.expandIcon, slots.endIcon, slotProps.collapseIcon, slotProps.expandIcon, slotProps.endIcon]);
  return (0, import_jsx_runtime.jsx)(TreeViewContext.Provider, {
    value: contextValue,
    children: (0, import_jsx_runtime.jsx)(TreeViewStyleContext.Provider, {
      value: styleContextValue,
      children: contextValue.wrapRoot({
        children
      })
    })
  });
}

// node_modules/@base-ui-components/utils/esm/useRefWithInit.js
var React4 = __toESM(require_react());
var UNINITIALIZED = {};
function useRefWithInit(init, initArg) {
  const ref = React4.useRef(UNINITIALIZED);
  if (ref.current === UNINITIALIZED) {
    ref.current = init(initArg);
  }
  return ref;
}

// node_modules/@mui/x-tree-view/node_modules/@mui/x-internals/esm/store/useStore.js
var import_with_selector = __toESM(require_with_selector(), 1);
function useStore(store, selector, a1, a2, a3) {
  const selectorWithArgs = (state) => selector(state, a1, a2, a3);
  return (0, import_with_selector.useSyncExternalStoreWithSelector)(store.subscribe, store.getSnapshot, store.getSnapshot, selectorWithArgs);
}

// node_modules/@mui/x-tree-view/node_modules/@mui/x-internals/esm/store/Store.js
var Store = class _Store {
  constructor(state) {
    __publicField(this, "subscribe", (fn) => {
      this.listeners.add(fn);
      return () => {
        this.listeners.delete(fn);
      };
    });
    __publicField(this, "getSnapshot", () => {
      return this.state;
    });
    this.state = state;
    this.listeners = /* @__PURE__ */ new Set();
    this.updateTick = 0;
  }
  // HACK: `any` fixes adding listeners that accept partial state.
  // Internal state to handle recursive `setState()` calls
  static create(state) {
    return new _Store(state);
  }
  setState(newState) {
    this.state = newState;
    this.updateTick += 1;
    const currentTick = this.updateTick;
    const it = this.listeners.values();
    let result;
    while (result = it.next(), !result.done) {
      if (currentTick !== this.updateTick) {
        return;
      }
      const listener = result.value;
      listener(newState);
    }
  }
  update(changes) {
    for (const key in changes) {
      if (!Object.is(this.state[key], changes[key])) {
        this.setState(_extends({}, this.state, changes));
        return;
      }
    }
  }
  set(key, value) {
    if (!Object.is(this.state[key], value)) {
      this.setState(_extends({}, this.state, {
        [key]: value
      }));
    }
  }
};

// node_modules/@mui/x-tree-view/node_modules/@mui/x-internals/esm/store/createSelector.js
var reselectCreateSelector = createSelectorCreator({
  memoize: lruMemoize,
  memoizeOptions: {
    maxSize: 1,
    equalityCheck: Object.is
  }
});
var createSelector = (a, b, c, d, e, f, ...other) => {
  if (other.length > 0) {
    throw new Error("Unsupported number of selectors");
  }
  let selector;
  if (a && b && c && d && e && f) {
    selector = (state, a1, a2, a3) => {
      const va = a(state, a1, a2, a3);
      const vb = b(state, a1, a2, a3);
      const vc = c(state, a1, a2, a3);
      const vd = d(state, a1, a2, a3);
      const ve = e(state, a1, a2, a3);
      return f(va, vb, vc, vd, ve, a1, a2, a3);
    };
  } else if (a && b && c && d && e) {
    selector = (state, a1, a2, a3) => {
      const va = a(state, a1, a2, a3);
      const vb = b(state, a1, a2, a3);
      const vc = c(state, a1, a2, a3);
      const vd = d(state, a1, a2, a3);
      return e(va, vb, vc, vd, a1, a2, a3);
    };
  } else if (a && b && c && d) {
    selector = (state, a1, a2, a3) => {
      const va = a(state, a1, a2, a3);
      const vb = b(state, a1, a2, a3);
      const vc = c(state, a1, a2, a3);
      return d(va, vb, vc, a1, a2, a3);
    };
  } else if (a && b && c) {
    selector = (state, a1, a2, a3) => {
      const va = a(state, a1, a2, a3);
      const vb = b(state, a1, a2, a3);
      return c(va, vb, a1, a2, a3);
    };
  } else if (a && b) {
    selector = (state, a1, a2, a3) => {
      const va = a(state, a1, a2, a3);
      return b(va, a1, a2, a3);
    };
  } else if (a) {
    selector = a;
  } else {
    throw new Error("Missing arguments");
  }
  return selector;
};
var createSelectorMemoized = (...inputs) => {
  const cache = /* @__PURE__ */ new WeakMap();
  let nextCacheId = 1;
  const combiner = inputs[inputs.length - 1];
  const nSelectors = inputs.length - 1 || 1;
  const argsLength = Math.max(combiner.length - nSelectors, 0);
  if (argsLength > 3) {
    throw new Error("Unsupported number of arguments");
  }
  const selector = (state, a1, a2, a3) => {
    let cacheKey = state.__cacheKey__;
    if (!cacheKey) {
      cacheKey = {
        id: nextCacheId
      };
      state.__cacheKey__ = cacheKey;
      nextCacheId += 1;
    }
    let fn = cache.get(cacheKey);
    if (!fn) {
      const selectors = inputs.length === 1 ? [(x) => x, combiner] : inputs;
      let reselectArgs = inputs;
      const selectorArgs = [void 0, void 0, void 0];
      switch (argsLength) {
        case 0:
          break;
        case 1: {
          reselectArgs = [...selectors.slice(0, -1), () => selectorArgs[0], combiner];
          break;
        }
        case 2: {
          reselectArgs = [...selectors.slice(0, -1), () => selectorArgs[0], () => selectorArgs[1], combiner];
          break;
        }
        case 3: {
          reselectArgs = [...selectors.slice(0, -1), () => selectorArgs[0], () => selectorArgs[1], () => selectorArgs[2], combiner];
          break;
        }
        default:
          throw new Error("Unsupported number of arguments");
      }
      fn = reselectCreateSelector(...reselectArgs);
      fn.selectorArgs = selectorArgs;
      cache.set(cacheKey, fn);
    }
    switch (argsLength) {
      case 3:
        fn.selectorArgs[2] = a3;
      case 2:
        fn.selectorArgs[1] = a2;
      case 1:
        fn.selectorArgs[0] = a1;
      case 0:
      default:
    }
    switch (argsLength) {
      case 0:
        return fn(state);
      case 1:
        return fn(state, a1);
      case 2:
        return fn(state, a1, a2);
      case 3:
        return fn(state, a1, a2, a3);
      default:
        throw new Error("unreachable");
    }
  };
  return selector;
};

// node_modules/@mui/x-tree-view/node_modules/@mui/x-internals/esm/store/useStoreEffect.js
var noop = () => {
};
function useStoreEffect(store, selector, effect) {
  const instance = useLazyRef(initialize, {
    store,
    selector
  }).current;
  instance.effect = effect;
  useOnMount(instance.onMount);
}
function initialize(params) {
  const {
    store,
    selector
  } = params;
  let previousState = selector(store.state);
  const instance = {
    effect: noop,
    dispose: null,
    // We want a single subscription done right away and cleared on unmount only,
    // but React triggers `useOnMount` multiple times in dev, so we need to manage
    // the subscription anyway.
    subscribe: () => {
      instance.dispose ?? (instance.dispose = store.subscribe((state) => {
        const nextState = selector(state);
        instance.effect(previousState, nextState);
        previousState = nextState;
      }));
    },
    onMount: () => {
      instance.subscribe();
      return () => {
        var _a;
        (_a = instance.dispose) == null ? void 0 : _a.call(instance);
        instance.dispose = null;
      };
    }
  };
  instance.subscribe();
  return instance;
}

// node_modules/@base-ui-components/utils/esm/useMergedRefs.js
function useMergedRefs(a, b, c, d) {
  const forkRef = useRefWithInit(createForkRef).current;
  if (didChange(forkRef, a, b, c, d)) {
    update(forkRef, [a, b, c, d]);
  }
  return forkRef.callback;
}
function createForkRef() {
  return {
    callback: null,
    cleanup: null,
    refs: []
  };
}
function didChange(forkRef, a, b, c, d) {
  return forkRef.refs[0] !== a || forkRef.refs[1] !== b || forkRef.refs[2] !== c || forkRef.refs[3] !== d;
}
function update(forkRef, refs) {
  forkRef.refs = refs;
  if (refs.every((ref) => ref == null)) {
    forkRef.callback = null;
    return;
  }
  forkRef.callback = (instance) => {
    if (forkRef.cleanup) {
      forkRef.cleanup();
      forkRef.cleanup = null;
    }
    if (instance != null) {
      const cleanupCallbacks = Array(refs.length).fill(null);
      for (let i = 0; i < refs.length; i += 1) {
        const ref = refs[i];
        if (ref == null) {
          continue;
        }
        switch (typeof ref) {
          case "function": {
            const refCleanup = ref(instance);
            if (typeof refCleanup === "function") {
              cleanupCallbacks[i] = refCleanup;
            }
            break;
          }
          case "object": {
            ref.current = instance;
            break;
          }
          default:
        }
      }
      forkRef.cleanup = () => {
        for (let i = 0; i < refs.length; i += 1) {
          const ref = refs[i];
          if (ref == null) {
            continue;
          }
          switch (typeof ref) {
            case "function": {
              const cleanupCallback = cleanupCallbacks[i];
              if (typeof cleanupCallback === "function") {
                cleanupCallback();
              } else {
                ref(null);
              }
              break;
            }
            case "object": {
              ref.current = null;
              break;
            }
            default:
          }
        }
      };
    }
  };
}

// node_modules/@mui/x-tree-view/esm/internals/corePlugins/useTreeViewId/useTreeViewId.selectors.js
var idSelectors = {
  /**
   * Get the id attribute of the tree view.
   * @param {TreeViewState<[UseTreeViewIdSignature]>} state The state of the tree view.
   * @returns {string} The id attribute of the tree view.
   */
  treeId: createSelector((state) => state.id.treeId)
};

// node_modules/@mui/x-tree-view/esm/internals/corePlugins/useTreeViewId/useTreeViewId.utils.js
var globalTreeViewDefaultId = 0;
var createTreeViewDefaultId = () => {
  globalTreeViewDefaultId += 1;
  return `mui-tree-view-${globalTreeViewDefaultId}`;
};
var generateTreeItemIdAttribute = ({
  id,
  treeId = "",
  itemId
}) => {
  if (id != null) {
    return id;
  }
  return `${treeId}-${itemId}`;
};

// node_modules/@mui/x-tree-view/esm/internals/corePlugins/useTreeViewId/useTreeViewId.js
var React5 = __toESM(require_react(), 1);
var useTreeViewId = ({
  params,
  store
}) => {
  React5.useEffect(() => {
    const prevIdState = store.state.id;
    if (params.id === prevIdState.providedTreeId && prevIdState.treeId !== void 0) {
      return;
    }
    store.set("id", _extends({}, prevIdState, {
      treeId: params.id ?? createTreeViewDefaultId()
    }));
  }, [store, params.id]);
  const treeId = useStore(store, idSelectors.treeId);
  return {
    getRootProps: () => ({
      id: treeId
    })
  };
};
useTreeViewId.params = {
  id: true
};
useTreeViewId.getInitialState = ({
  id
}) => ({
  id: {
    treeId: void 0,
    providedTreeId: id
  }
});

// node_modules/@mui/x-tree-view/esm/internals/TreeViewItemDepthContext/TreeViewItemDepthContext.js
var React6 = __toESM(require_react(), 1);
var TreeViewItemDepthContext = React6.createContext(() => -1);
if (true) TreeViewItemDepthContext.displayName = "TreeViewItemDepthContext";

// node_modules/@mui/x-tree-view/esm/internals/plugins/useTreeViewItems/useTreeViewItems.utils.js
var TREE_VIEW_ROOT_PARENT_ID = "__TREE_VIEW_ROOT_PARENT_ID__";
var buildSiblingIndexes = (siblings) => {
  const siblingsIndexLookup = {};
  siblings.forEach((childId, index) => {
    siblingsIndexLookup[childId] = index;
  });
  return siblingsIndexLookup;
};
var isItemDisabled = (itemMetaLookup, itemId) => {
  if (itemId == null) {
    return false;
  }
  let itemMeta = itemMetaLookup[itemId];
  if (!itemMeta) {
    return false;
  }
  if (itemMeta.disabled) {
    return true;
  }
  while (itemMeta.parentId != null) {
    itemMeta = itemMetaLookup[itemMeta.parentId];
    if (!itemMeta) {
      return false;
    }
    if (itemMeta.disabled) {
      return true;
    }
  }
  return false;
};
function buildItemsState(parameters) {
  const {
    config,
    items: itemsParam,
    disabledItemsFocusable
  } = parameters;
  const itemMetaLookup = {};
  const itemModelLookup = {};
  const itemOrderedChildrenIdsLookup = {};
  const itemChildrenIndexesLookup = {};
  function processSiblings(items, parentId, depth) {
    const parentIdWithDefault = parentId ?? TREE_VIEW_ROOT_PARENT_ID;
    const {
      metaLookup,
      modelLookup,
      orderedChildrenIds,
      childrenIndexes,
      itemsChildren
    } = buildItemsLookups({
      config,
      items,
      parentId,
      depth,
      isItemExpandable: (item, children) => !!children && children.length > 0,
      otherItemsMetaLookup: itemMetaLookup
    });
    Object.assign(itemMetaLookup, metaLookup);
    Object.assign(itemModelLookup, modelLookup);
    itemOrderedChildrenIdsLookup[parentIdWithDefault] = orderedChildrenIds;
    itemChildrenIndexesLookup[parentIdWithDefault] = childrenIndexes;
    for (const item of itemsChildren) {
      processSiblings(item.children || [], item.id, depth + 1);
    }
  }
  processSiblings(itemsParam, null, 0);
  return {
    disabledItemsFocusable,
    itemMetaLookup,
    itemModelLookup,
    itemOrderedChildrenIdsLookup,
    itemChildrenIndexesLookup,
    domStructure: "nested"
  };
}
function buildItemsLookups(parameters) {
  const {
    config,
    items,
    parentId,
    depth,
    isItemExpandable,
    otherItemsMetaLookup
  } = parameters;
  const metaLookup = {};
  const modelLookup = {};
  const orderedChildrenIds = [];
  const itemsChildren = [];
  const processItem = (item) => {
    const id = config.getItemId ? config.getItemId(item) : item.id;
    checkId({
      id,
      parentId,
      item,
      itemMetaLookup: otherItemsMetaLookup,
      siblingsMetaLookup: metaLookup
    });
    const label = config.getItemLabel ? config.getItemLabel(item) : item.label;
    if (label == null) {
      throw new Error(["MUI X: The Tree View component requires all items to have a `label` property.", "Alternatively, you can use the `getItemLabel` prop to specify a custom label for each item.", "An item was provided without label in the `items` prop:", JSON.stringify(item)].join("\n"));
    }
    const children = (config.getItemChildren ? config.getItemChildren(item) : item.children) || [];
    itemsChildren.push({
      id,
      children
    });
    modelLookup[id] = item;
    metaLookup[id] = {
      id,
      label,
      parentId,
      idAttribute: void 0,
      expandable: isItemExpandable(item, children),
      disabled: config.isItemDisabled ? config.isItemDisabled(item) : false,
      depth
    };
    orderedChildrenIds.push(id);
  };
  for (const item of items) {
    processItem(item);
  }
  return {
    metaLookup,
    modelLookup,
    orderedChildrenIds,
    childrenIndexes: buildSiblingIndexes(orderedChildrenIds),
    itemsChildren
  };
}
function checkId({
  id,
  parentId,
  item,
  itemMetaLookup,
  siblingsMetaLookup
}) {
  if (id == null) {
    throw new Error(["MUI X: The Tree View component requires all items to have a unique `id` property.", "Alternatively, you can use the `getItemId` prop to specify a custom id for each item.", "An item was provided without id in the `items` prop:", JSON.stringify(item)].join("\n"));
  }
  if (siblingsMetaLookup[id] != null || // Ignore items with the same parent id, because it's the same item from the previous generation.
  itemMetaLookup[id] != null && itemMetaLookup[id].parentId !== parentId) {
    throw new Error(["MUI X: The Tree View component requires all items to have a unique `id` property.", "Alternatively, you can use the `getItemId` prop to specify a custom id for each item.", `Two items were provided with the same id in the \`items\` prop: "${id}"`].join("\n"));
  }
}

// node_modules/@mui/x-tree-view/esm/internals/plugins/useTreeViewItems/useTreeViewItems.selectors.js
var EMPTY_CHILDREN = [];
var itemsSelectors = {
  /**
   * Gets the DOM structure of the Tree View.
   */
  domStructure: createSelector((state) => state.items.domStructure),
  /**
   * Checks whether the disabled items are focusable.
   */
  disabledItemFocusable: createSelector((state) => state.items.disabledItemsFocusable),
  /**
   * Gets the meta-information of all items.
   */
  itemMetaLookup: createSelector((state) => state.items.itemMetaLookup),
  /**
   * Gets the ordered children ids of all items.
   */
  itemOrderedChildrenIdsLookup: createSelector((state) => state.items.itemOrderedChildrenIdsLookup),
  /**
   * Gets the meta-information of an item.
   */
  itemMeta: createSelector((state, itemId) => state.items.itemMetaLookup[itemId ?? TREE_VIEW_ROOT_PARENT_ID] ?? null),
  /**
   * Gets the ordered children ids of an item.
   */
  itemOrderedChildrenIds: createSelector((state, itemId) => state.items.itemOrderedChildrenIdsLookup[itemId ?? TREE_VIEW_ROOT_PARENT_ID] ?? EMPTY_CHILDREN),
  /**
   * Gets the model of an item.
   */
  itemModel: createSelector((state, itemId) => state.items.itemModelLookup[itemId]),
  /**
   * Checks whether an item is disabled.
   */
  isItemDisabled: createSelector((state, itemId) => isItemDisabled(state.items.itemMetaLookup, itemId)),
  /**
   * Gets the index of an item in its parent's children.
   */
  itemIndex: createSelector((state, itemId) => {
    const itemMeta = state.items.itemMetaLookup[itemId];
    if (itemMeta == null) {
      return -1;
    }
    const parentIndexes = state.items.itemChildrenIndexesLookup[itemMeta.parentId ?? TREE_VIEW_ROOT_PARENT_ID];
    return parentIndexes[itemMeta.id];
  }),
  /**
   * Gets the id of an item's parent.
   */
  itemParentId: createSelector((state, itemId) => {
    var _a;
    return ((_a = state.items.itemMetaLookup[itemId]) == null ? void 0 : _a.parentId) ?? null;
  }),
  /**
   * Gets the depth of an item (items at the root level have a depth of 0).
   */
  itemDepth: createSelector((state, itemId) => {
    var _a;
    return ((_a = state.items.itemMetaLookup[itemId]) == null ? void 0 : _a.depth) ?? 0;
  }),
  /**
   * Checks whether an item can be focused.
   */
  canItemBeFocused: createSelector((state, itemId) => state.items.disabledItemsFocusable || !isItemDisabled(state.items.itemMetaLookup, itemId))
};

// node_modules/@mui/x-tree-view/esm/internals/plugins/useTreeViewItems/useTreeViewItems.js
var React8 = __toESM(require_react(), 1);

// node_modules/@base-ui-components/utils/esm/useEventCallback.js
var React7 = __toESM(require_react());
var useInsertionEffect = React7[`useInsertionEffect${Math.random().toFixed(1)}`.slice(0, -3)];
var useSafeInsertionEffect = (
  // React 17 doesn't have useInsertionEffect.
  useInsertionEffect && // Preact replaces useInsertionEffect with useLayoutEffect and fires too late.
  useInsertionEffect !== React7.useLayoutEffect ? useInsertionEffect : (fn) => fn()
);
function useEventCallback(callback) {
  const stable = useRefWithInit(createStableCallback).current;
  stable.next = callback;
  useSafeInsertionEffect(stable.effect);
  return stable.trampoline;
}
function createStableCallback() {
  const stable = {
    next: void 0,
    callback: assertNotCalled,
    trampoline: (...args) => {
      var _a;
      return (_a = stable.callback) == null ? void 0 : _a.call(stable, ...args);
    },
    effect: () => {
      stable.callback = stable.next;
    }
  };
  return stable;
}
function assertNotCalled() {
  if (true) {
    throw new Error("Base UI: Cannot call an event handler while rendering.");
  }
}

// node_modules/@mui/x-tree-view/esm/internals/plugins/useTreeViewItems/useTreeViewItems.js
var import_jsx_runtime2 = __toESM(require_jsx_runtime(), 1);
var useTreeViewItems = ({
  instance,
  params,
  store
}) => {
  const itemsConfig = React8.useMemo(() => ({
    isItemDisabled: params.isItemDisabled,
    getItemLabel: params.getItemLabel,
    getItemChildren: params.getItemChildren,
    getItemId: params.getItemId
  }), [params.isItemDisabled, params.getItemLabel, params.getItemChildren, params.getItemId]);
  const getItem = React8.useCallback((itemId) => itemsSelectors.itemModel(store.state, itemId), [store]);
  const getParentId = React8.useCallback((itemId) => {
    const itemMeta = itemsSelectors.itemMeta(store.state, itemId);
    return (itemMeta == null ? void 0 : itemMeta.parentId) || null;
  }, [store]);
  const setIsItemDisabled = useEventCallback(({
    itemId,
    shouldBeDisabled
  }) => {
    if (!store.state.items.itemMetaLookup[itemId]) {
      return;
    }
    const itemMetaLookup = _extends({}, store.state.items.itemMetaLookup);
    itemMetaLookup[itemId] = _extends({}, itemMetaLookup[itemId], {
      disabled: shouldBeDisabled ?? !itemMetaLookup[itemId].disabled
    });
    store.set("items", _extends({}, store.state.items, {
      itemMetaLookup
    }));
  });
  const getItemTree = React8.useCallback(() => {
    const getItemFromItemId = (itemId) => {
      const item = itemsSelectors.itemModel(store.state, itemId);
      const itemToMutate = _extends({}, item);
      const newChildren = itemsSelectors.itemOrderedChildrenIds(store.state, itemId);
      if (newChildren.length > 0) {
        itemToMutate.children = newChildren.map(getItemFromItemId);
      } else {
        delete itemToMutate.children;
      }
      return itemToMutate;
    };
    return itemsSelectors.itemOrderedChildrenIds(store.state, null).map(getItemFromItemId);
  }, [store]);
  const getItemOrderedChildrenIds = React8.useCallback((itemId) => itemsSelectors.itemOrderedChildrenIds(store.state, itemId), [store]);
  const getItemDOMElement = (itemId) => {
    const itemMeta = itemsSelectors.itemMeta(store.state, itemId);
    if (itemMeta == null) {
      return null;
    }
    const idAttribute = generateTreeItemIdAttribute({
      treeId: idSelectors.treeId(store.state),
      itemId,
      id: itemMeta.idAttribute
    });
    return document.getElementById(idAttribute);
  };
  const areItemUpdatesPreventedRef = React8.useRef(false);
  const preventItemUpdates = React8.useCallback(() => {
    areItemUpdatesPreventedRef.current = true;
  }, []);
  const areItemUpdatesPrevented = React8.useCallback(() => areItemUpdatesPreventedRef.current, []);
  const setItemChildren = ({
    items,
    parentId,
    getChildrenCount
  }) => {
    const parentIdWithDefault = parentId ?? TREE_VIEW_ROOT_PARENT_ID;
    const parentDepth = parentId == null ? -1 : itemsSelectors.itemDepth(store.state, parentId);
    const {
      metaLookup,
      modelLookup,
      orderedChildrenIds,
      childrenIndexes
    } = buildItemsLookups({
      config: itemsConfig,
      items,
      parentId,
      depth: parentDepth + 1,
      isItemExpandable: getChildrenCount ? (item) => getChildrenCount(item) > 0 : () => false,
      otherItemsMetaLookup: itemsSelectors.itemMetaLookup(store.state)
    });
    const lookups = {
      itemModelLookup: _extends({}, store.state.items.itemModelLookup, modelLookup),
      itemMetaLookup: _extends({}, store.state.items.itemMetaLookup, metaLookup),
      itemOrderedChildrenIdsLookup: _extends({}, store.state.items.itemOrderedChildrenIdsLookup, {
        [parentIdWithDefault]: orderedChildrenIds
      }),
      itemChildrenIndexesLookup: _extends({}, store.state.items.itemChildrenIndexesLookup, {
        [parentIdWithDefault]: childrenIndexes
      })
    };
    store.set("items", _extends({}, store.state.items, lookups));
  };
  const removeChildren = useEventCallback((parentId) => {
    const newMetaMap = Object.keys(store.state.items.itemMetaLookup).reduce((acc, key) => {
      const item = store.state.items.itemMetaLookup[key];
      if (item.parentId === parentId) {
        return acc;
      }
      return _extends({}, acc, {
        [item.id]: item
      });
    }, {});
    const newItemOrderedChildrenIdsLookup = _extends({}, store.state.items.itemOrderedChildrenIdsLookup);
    const newItemChildrenIndexesLookup = _extends({}, store.state.items.itemChildrenIndexesLookup);
    const cleanId = parentId ?? TREE_VIEW_ROOT_PARENT_ID;
    delete newItemChildrenIndexesLookup[cleanId];
    delete newItemOrderedChildrenIdsLookup[cleanId];
    store.set("items", _extends({}, store.state.items, {
      itemMetaLookup: newMetaMap,
      itemOrderedChildrenIdsLookup: newItemOrderedChildrenIdsLookup,
      itemChildrenIndexesLookup: newItemChildrenIndexesLookup
    }));
  });
  const addExpandableItems = useEventCallback((items) => {
    const newItemMetaLookup = _extends({}, store.state.items.itemMetaLookup);
    for (const itemId of items) {
      newItemMetaLookup[itemId] = _extends({}, newItemMetaLookup[itemId], {
        expandable: true
      });
    }
    store.set("items", _extends({}, store.state.items, {
      itemMetaLookup: newItemMetaLookup
    }));
  });
  React8.useEffect(() => {
    if (instance.areItemUpdatesPrevented()) {
      return;
    }
    const newState = buildItemsState({
      disabledItemsFocusable: params.disabledItemsFocusable,
      items: params.items,
      config: itemsConfig
    });
    store.set("items", _extends({}, store.state.items, newState));
  }, [instance, store, params.items, params.disabledItemsFocusable, itemsConfig]);
  const handleItemClick = useEventCallback((event, itemId) => {
    if (params.onItemClick) {
      params.onItemClick(event, itemId);
    }
  });
  return {
    getRootProps: () => ({
      style: {
        "--TreeView-itemChildrenIndentation": typeof params.itemChildrenIndentation === "number" ? `${params.itemChildrenIndentation}px` : params.itemChildrenIndentation
      }
    }),
    publicAPI: {
      getItem,
      getItemDOMElement,
      getItemTree,
      getItemOrderedChildrenIds,
      setIsItemDisabled,
      getParentId
    },
    instance: {
      getItemDOMElement,
      preventItemUpdates,
      areItemUpdatesPrevented,
      setItemChildren,
      removeChildren,
      addExpandableItems,
      handleItemClick
    }
  };
};
useTreeViewItems.getInitialState = (params) => ({
  items: buildItemsState({
    items: params.items,
    disabledItemsFocusable: params.disabledItemsFocusable,
    config: {
      isItemDisabled: params.isItemDisabled,
      getItemId: params.getItemId,
      getItemLabel: params.getItemLabel,
      getItemChildren: params.getItemChildren
    }
  })
});
useTreeViewItems.applyDefaultValuesToParams = ({
  params
}) => _extends({}, params, {
  disabledItemsFocusable: params.disabledItemsFocusable ?? false,
  itemChildrenIndentation: params.itemChildrenIndentation ?? "12px"
});
useTreeViewItems.wrapRoot = ({
  children
}) => {
  return (0, import_jsx_runtime2.jsx)(TreeViewItemDepthContext.Provider, {
    value: itemsSelectors.itemDepth,
    children
  });
};
if (true) useTreeViewItems.wrapRoot.displayName = "useTreeViewItems.wrapRoot";
useTreeViewItems.params = {
  disabledItemsFocusable: true,
  items: true,
  isItemDisabled: true,
  getItemLabel: true,
  getItemChildren: true,
  getItemId: true,
  onItemClick: true,
  itemChildrenIndentation: true
};

// node_modules/@mui/x-tree-view/esm/internals/plugins/useTreeViewExpansion/useTreeViewExpansion.selectors.js
var expandedItemMapSelector = createSelectorMemoized((state) => state.expansion.expandedItems, (expandedItems) => {
  const expandedItemsMap = /* @__PURE__ */ new Map();
  expandedItems.forEach((id) => {
    expandedItemsMap.set(id, true);
  });
  return expandedItemsMap;
});
var expansionSelectors = {
  /**
   * Gets the expanded items as provided to the component.
   */
  expandedItemsRaw: createSelector((state) => state.expansion.expandedItems),
  /**
   * Gets the expanded items as a Map.
   */
  expandedItemsMap: expandedItemMapSelector,
  /**
   * Gets the items to render as a flat list (the descendants of an expanded item are listed as siblings of the item).
   */
  flatList: createSelectorMemoized(itemsSelectors.itemOrderedChildrenIdsLookup, expandedItemMapSelector, (itemOrderedChildrenIds, expandedItemsMap) => {
    function appendChildren(itemId) {
      if (!expandedItemsMap.has(itemId)) {
        return [itemId];
      }
      const itemsWithDescendants = [itemId];
      const children = itemOrderedChildrenIds[itemId] || [];
      for (const childId of children) {
        itemsWithDescendants.push(...appendChildren(childId));
      }
      return itemsWithDescendants;
    }
    return (itemOrderedChildrenIds[TREE_VIEW_ROOT_PARENT_ID] ?? []).flatMap(appendChildren);
  }),
  /**
   * Gets the slot that triggers the item's expansion when clicked.
   */
  triggerSlot: createSelector((state) => state.expansion.expansionTrigger),
  /**
   * Checks whether an item is expanded.
   */
  isItemExpanded: createSelector(expandedItemMapSelector, (expandedItemsMap, itemId) => expandedItemsMap.has(itemId)),
  /**
   * Checks whether an item is expandable.
   */
  isItemExpandable: createSelector(itemsSelectors.itemMeta, (itemMeta, _itemId) => (itemMeta == null ? void 0 : itemMeta.expandable) ?? false)
};

// node_modules/@mui/x-tree-view/node_modules/@mui/x-internals/esm/useAssertModelConsistency/useAssertModelConsistency.js
var React9 = __toESM(require_react(), 1);
function useAssertModelConsistencyOutsideOfProduction(parameters) {
  const {
    componentName,
    propName,
    controlled,
    defaultValue,
    warningPrefix = "MUI X"
  } = parameters;
  const [{
    initialDefaultValue,
    isControlled
  }] = React9.useState({
    initialDefaultValue: defaultValue,
    isControlled: controlled !== void 0
  });
  if (isControlled !== (controlled !== void 0)) {
    warnOnce([`${warningPrefix}: A component is changing the ${isControlled ? "" : "un"}controlled ${propName} state of ${componentName} to be ${isControlled ? "un" : ""}controlled.`, "Elements should not switch from uncontrolled to controlled (or vice versa).", `Decide between using a controlled or uncontrolled ${propName} element for the lifetime of the component.`, "The nature of the state is determined during the first render. It's considered controlled if the value is not `undefined`.", "More info: https://fb.me/react-controlled-components"], "error");
  }
  if (JSON.stringify(initialDefaultValue) !== JSON.stringify(defaultValue)) {
    warnOnce([`${warningPrefix}: A component is changing the default ${propName} state of an uncontrolled ${componentName} after being initialized. To suppress this warning opt to use a controlled ${componentName}.`], "error");
  }
}
var useAssertModelConsistency = false ? () => {
} : useAssertModelConsistencyOutsideOfProduction;

// node_modules/@base-ui-components/utils/esm/useIsoLayoutEffect.js
var React10 = __toESM(require_react());
var noop2 = () => {
};
var useIsoLayoutEffect = typeof document !== "undefined" ? React10.useLayoutEffect : noop2;

// node_modules/@mui/x-tree-view/esm/internals/plugins/useTreeViewExpansion/useTreeViewExpansion.utils.js
var getExpansionTrigger = ({
  isItemEditable,
  expansionTrigger
}) => {
  if (expansionTrigger) {
    return expansionTrigger;
  }
  if (isItemEditable) {
    return "iconContainer";
  }
  return "content";
};

// node_modules/@mui/x-tree-view/esm/internals/utils/publishTreeViewEvent.js
var publishTreeViewEvent = (instance, eventName, params) => {
  instance.$$publishEvent(eventName, params);
};

// node_modules/@mui/x-tree-view/esm/internals/plugins/useTreeViewExpansion/useTreeViewExpansion.js
var useTreeViewExpansion = ({
  instance,
  store,
  params
}) => {
  useAssertModelConsistency({
    componentName: "Tree View",
    propName: "expandedItems",
    controlled: params.expandedItems,
    defaultValue: params.defaultExpandedItems
  });
  useIsoLayoutEffect(() => {
    const newExpansionTrigger = getExpansionTrigger({
      isItemEditable: params.isItemEditable,
      expansionTrigger: params.expansionTrigger
    });
    if (store.state.expansion.expansionTrigger === newExpansionTrigger) {
      return;
    }
    store.set("expansion", _extends({}, store.state.expansion, {
      expansionTrigger: newExpansionTrigger
    }));
  }, [store, params.isItemEditable, params.expansionTrigger]);
  const setExpandedItems = (event, value) => {
    var _a;
    if (params.expandedItems === void 0) {
      store.set("expansion", _extends({}, store.state.expansion, {
        expandedItems: value
      }));
    }
    (_a = params.onExpandedItemsChange) == null ? void 0 : _a.call(params, event, value);
  };
  const resetItemExpansion = useEventCallback(() => {
    setExpandedItems(null, []);
  });
  const applyItemExpansion = useEventCallback(({
    itemId,
    event,
    shouldBeExpanded
  }) => {
    const oldExpanded = expansionSelectors.expandedItemsRaw(store.state);
    let newExpanded;
    if (shouldBeExpanded) {
      newExpanded = [itemId].concat(oldExpanded);
    } else {
      newExpanded = oldExpanded.filter((id) => id !== itemId);
    }
    if (params.onItemExpansionToggle) {
      params.onItemExpansionToggle(event, itemId, shouldBeExpanded);
    }
    setExpandedItems(event, newExpanded);
  });
  const setItemExpansion = useEventCallback(({
    itemId,
    event = null,
    shouldBeExpanded
  }) => {
    const isExpandedBefore = expansionSelectors.isItemExpanded(store.state, itemId);
    const cleanShouldBeExpanded = shouldBeExpanded ?? !isExpandedBefore;
    if (isExpandedBefore === cleanShouldBeExpanded) {
      return;
    }
    const eventParameters = {
      isExpansionPrevented: false,
      shouldBeExpanded: cleanShouldBeExpanded,
      event,
      itemId
    };
    publishTreeViewEvent(instance, "beforeItemToggleExpansion", eventParameters);
    if (eventParameters.isExpansionPrevented) {
      return;
    }
    instance.applyItemExpansion({
      itemId,
      event,
      shouldBeExpanded: cleanShouldBeExpanded
    });
  });
  const isItemExpanded = useEventCallback((itemId) => {
    return expansionSelectors.isItemExpanded(store.state, itemId);
  });
  const expandAllSiblings = (event, itemId) => {
    const itemMeta = itemsSelectors.itemMeta(store.state, itemId);
    if (itemMeta == null) {
      return;
    }
    const siblings = itemsSelectors.itemOrderedChildrenIds(store.state, itemMeta.parentId);
    const diff = siblings.filter((child) => expansionSelectors.isItemExpandable(store.state, child) && !expansionSelectors.isItemExpanded(store.state, child));
    const newExpanded = expansionSelectors.expandedItemsRaw(store.state).concat(diff);
    if (diff.length > 0) {
      if (params.onItemExpansionToggle) {
        diff.forEach((newlyExpandedItemId) => {
          params.onItemExpansionToggle(event, newlyExpandedItemId, true);
        });
      }
      setExpandedItems(event, newExpanded);
    }
  };
  useIsoLayoutEffect(() => {
    const expandedItems = params.expandedItems;
    if (expandedItems !== void 0) {
      store.set("expansion", _extends({}, store.state.expansion, {
        expandedItems
      }));
    }
  }, [store, params.expandedItems]);
  return {
    publicAPI: {
      setItemExpansion,
      isItemExpanded
    },
    instance: {
      setItemExpansion,
      applyItemExpansion,
      expandAllSiblings,
      resetItemExpansion
    }
  };
};
var DEFAULT_EXPANDED_ITEMS = [];
useTreeViewExpansion.applyDefaultValuesToParams = ({
  params
}) => _extends({}, params, {
  defaultExpandedItems: params.defaultExpandedItems ?? DEFAULT_EXPANDED_ITEMS
});
useTreeViewExpansion.getInitialState = (params) => ({
  expansion: {
    expandedItems: params.expandedItems === void 0 ? params.defaultExpandedItems : params.expandedItems,
    expansionTrigger: getExpansionTrigger(params)
  }
});
useTreeViewExpansion.params = {
  expandedItems: true,
  defaultExpandedItems: true,
  onExpandedItemsChange: true,
  onItemExpansionToggle: true,
  expansionTrigger: true
};

// node_modules/@mui/x-tree-view/esm/internals/utils/tree.js
var getLastNavigableItemInArray = (state, items) => {
  let itemIndex = items.length - 1;
  while (itemIndex >= 0 && !itemsSelectors.canItemBeFocused(state, items[itemIndex])) {
    itemIndex -= 1;
  }
  if (itemIndex === -1) {
    return void 0;
  }
  return items[itemIndex];
};
var getPreviousNavigableItem = (state, itemId) => {
  const itemMeta = itemsSelectors.itemMeta(state, itemId);
  if (!itemMeta) {
    return null;
  }
  const siblings = itemsSelectors.itemOrderedChildrenIds(state, itemMeta.parentId);
  const itemIndex = itemsSelectors.itemIndex(state, itemId);
  if (itemIndex === 0) {
    return itemMeta.parentId;
  }
  let previousNavigableSiblingIndex = itemIndex - 1;
  while (!itemsSelectors.canItemBeFocused(state, siblings[previousNavigableSiblingIndex]) && previousNavigableSiblingIndex >= 0) {
    previousNavigableSiblingIndex -= 1;
  }
  if (previousNavigableSiblingIndex === -1) {
    if (itemMeta.parentId == null) {
      return null;
    }
    return getPreviousNavigableItem(state, itemMeta.parentId);
  }
  let currentItemId = siblings[previousNavigableSiblingIndex];
  let lastNavigableChild = getLastNavigableItemInArray(state, itemsSelectors.itemOrderedChildrenIds(state, currentItemId));
  while (expansionSelectors.isItemExpanded(state, currentItemId) && lastNavigableChild != null) {
    currentItemId = lastNavigableChild;
    lastNavigableChild = getLastNavigableItemInArray(state, itemsSelectors.itemOrderedChildrenIds(state, currentItemId));
  }
  return currentItemId;
};
var getNextNavigableItem = (state, itemId) => {
  if (expansionSelectors.isItemExpanded(state, itemId)) {
    const firstNavigableChild = itemsSelectors.itemOrderedChildrenIds(state, itemId).find((childId) => itemsSelectors.canItemBeFocused(state, childId));
    if (firstNavigableChild != null) {
      return firstNavigableChild;
    }
  }
  let itemMeta = itemsSelectors.itemMeta(state, itemId);
  while (itemMeta != null) {
    const siblings = itemsSelectors.itemOrderedChildrenIds(state, itemMeta.parentId);
    const currentItemIndex = itemsSelectors.itemIndex(state, itemMeta.id);
    if (currentItemIndex < siblings.length - 1) {
      let nextItemIndex = currentItemIndex + 1;
      while (!itemsSelectors.canItemBeFocused(state, siblings[nextItemIndex]) && nextItemIndex < siblings.length - 1) {
        nextItemIndex += 1;
      }
      if (itemsSelectors.canItemBeFocused(state, siblings[nextItemIndex])) {
        return siblings[nextItemIndex];
      }
    }
    itemMeta = itemsSelectors.itemMeta(state, itemMeta.parentId);
  }
  return null;
};
var getLastNavigableItem = (state) => {
  let itemId = null;
  while (itemId == null || expansionSelectors.isItemExpanded(state, itemId)) {
    const children = itemsSelectors.itemOrderedChildrenIds(state, itemId);
    const lastNavigableChild = getLastNavigableItemInArray(state, children);
    if (lastNavigableChild == null) {
      return itemId;
    }
    itemId = lastNavigableChild;
  }
  return itemId;
};
var getFirstNavigableItem = (state) => itemsSelectors.itemOrderedChildrenIds(state, null).find((itemId) => itemsSelectors.canItemBeFocused(state, itemId));
var findOrderInTremauxTree = (state, itemAId, itemBId) => {
  if (itemAId === itemBId) {
    return [itemAId, itemBId];
  }
  const itemMetaA = itemsSelectors.itemMeta(state, itemAId);
  const itemMetaB = itemsSelectors.itemMeta(state, itemBId);
  if (!itemMetaA || !itemMetaB) {
    return [itemAId, itemBId];
  }
  if (itemMetaA.parentId === itemMetaB.id || itemMetaB.parentId === itemMetaA.id) {
    return itemMetaB.parentId === itemMetaA.id ? [itemMetaA.id, itemMetaB.id] : [itemMetaB.id, itemMetaA.id];
  }
  const aFamily = [itemMetaA.id];
  const bFamily = [itemMetaB.id];
  let aAncestor = itemMetaA.parentId;
  let bAncestor = itemMetaB.parentId;
  let aAncestorIsCommon = bFamily.indexOf(aAncestor) !== -1;
  let bAncestorIsCommon = aFamily.indexOf(bAncestor) !== -1;
  let continueA = true;
  let continueB = true;
  while (!bAncestorIsCommon && !aAncestorIsCommon) {
    if (continueA) {
      aFamily.push(aAncestor);
      aAncestorIsCommon = bFamily.indexOf(aAncestor) !== -1;
      continueA = aAncestor !== null;
      if (!aAncestorIsCommon && continueA) {
        aAncestor = itemsSelectors.itemParentId(state, aAncestor);
      }
    }
    if (continueB && !aAncestorIsCommon) {
      bFamily.push(bAncestor);
      bAncestorIsCommon = aFamily.indexOf(bAncestor) !== -1;
      continueB = bAncestor !== null;
      if (!bAncestorIsCommon && continueB) {
        bAncestor = itemsSelectors.itemParentId(state, bAncestor);
      }
    }
  }
  const commonAncestor = aAncestorIsCommon ? aAncestor : bAncestor;
  const ancestorFamily = itemsSelectors.itemOrderedChildrenIds(state, commonAncestor);
  const aSide = aFamily[aFamily.indexOf(commonAncestor) - 1];
  const bSide = bFamily[bFamily.indexOf(commonAncestor) - 1];
  return ancestorFamily.indexOf(aSide) < ancestorFamily.indexOf(bSide) ? [itemAId, itemBId] : [itemBId, itemAId];
};
var getNonDisabledItemsInRange = (state, itemAId, itemBId) => {
  const getNextItem = (itemId) => {
    if (expansionSelectors.isItemExpandable(state, itemId) && expansionSelectors.isItemExpanded(state, itemId)) {
      return itemsSelectors.itemOrderedChildrenIds(state, itemId)[0];
    }
    let itemMeta = itemsSelectors.itemMeta(state, itemId);
    while (itemMeta != null) {
      const siblings = itemsSelectors.itemOrderedChildrenIds(state, itemMeta.parentId);
      const currentItemIndex = itemsSelectors.itemIndex(state, itemMeta.id);
      if (currentItemIndex < siblings.length - 1) {
        return siblings[currentItemIndex + 1];
      }
      itemMeta = itemMeta.parentId ? itemsSelectors.itemMeta(state, itemMeta.parentId) : null;
    }
    throw new Error("Invalid range");
  };
  const [first, last] = findOrderInTremauxTree(state, itemAId, itemBId);
  const items = [first];
  let current = first;
  while (current !== last) {
    current = getNextItem(current);
    if (!itemsSelectors.isItemDisabled(state, current)) {
      items.push(current);
    }
  }
  return items;
};
var getAllNavigableItems = (state) => {
  let item = getFirstNavigableItem(state);
  const navigableItems = [];
  while (item != null) {
    navigableItems.push(item);
    item = getNextNavigableItem(state, item);
  }
  return navigableItems;
};
var isTargetInDescendants = (target, itemRoot) => {
  return itemRoot !== target.closest('*[role="treeitem"]');
};

// node_modules/@mui/x-tree-view/esm/internals/plugins/useTreeViewSelection/useTreeViewSelection.selectors.js
var selectedItemsSelector = createSelectorMemoized((state) => state.selection.selectedItems, (selectedItemsRaw) => {
  if (Array.isArray(selectedItemsRaw)) {
    return selectedItemsRaw;
  }
  if (selectedItemsRaw != null) {
    return [selectedItemsRaw];
  }
  return [];
});
var selectedItemsMapSelector = createSelectorMemoized(selectedItemsSelector, (selectedItems) => {
  const selectedItemsMap = /* @__PURE__ */ new Map();
  selectedItems.forEach((id) => {
    selectedItemsMap.set(id, true);
  });
  return selectedItemsMap;
});
var selectionSelectors = {
  /**
   * Gets the selected items as provided to the component.
   */
  selectedItemsRaw: createSelector((state) => state.selection.selectedItems),
  /**
   * Gets the selected items as an array.
   */
  selectedItems: selectedItemsSelector,
  /**
   * Gets the selected items as a Map.
   */
  selectedItemsMap: selectedItemsMapSelector,
  /**
   * Checks whether selection is enabled.
   */
  enabled: createSelector((state) => state.selection.isEnabled),
  /**
   * Checks whether multi selection is enabled.
   */
  isMultiSelectEnabled: createSelector((state) => state.selection.isMultiSelectEnabled),
  /**
   * Checks whether checkbox selection is enabled.
   */
  isCheckboxSelectionEnabled: createSelector((state) => state.selection.isCheckboxSelectionEnabled),
  /**
   * Gets the selection propagation rules.
   */
  propagationRules: createSelector((state) => state.selection.selectionPropagation),
  /**
   * Checks whether an item is selected.
   */
  isItemSelected: createSelector(selectedItemsMapSelector, (selectedItemsMap, itemId) => selectedItemsMap.has(itemId)),
  /**
   * Checks whether an item can be selected (if selection is enabled and if the item is not disabled).
   */
  canItemBeSelected: createSelector(itemsSelectors.isItemDisabled, (state) => state.selection.isEnabled, (isItemDisabled2, isSelectionEnabled, _itemId) => isSelectionEnabled && !isItemDisabled2)
};

// node_modules/@mui/x-tree-view/esm/internals/plugins/useTreeViewSelection/useTreeViewSelection.js
var React11 = __toESM(require_react(), 1);

// node_modules/@mui/x-tree-view/esm/internals/plugins/useTreeViewSelection/useTreeViewSelection.utils.js
var getLookupFromArray = (array) => {
  const lookup = {};
  array.forEach((itemId) => {
    lookup[itemId] = true;
  });
  return lookup;
};
var getAddedAndRemovedItems = ({
  store,
  oldModel,
  newModel
}) => {
  const newModelMap = /* @__PURE__ */ new Map();
  newModel.forEach((id) => {
    newModelMap.set(id, true);
  });
  return {
    added: newModel.filter((itemId) => !selectionSelectors.isItemSelected(store.state, itemId)),
    removed: oldModel.filter((itemId) => !newModelMap.has(itemId))
  };
};
var propagateSelection = ({
  store,
  selectionPropagation,
  newModel,
  oldModel,
  additionalItemsToPropagate
}) => {
  if (!selectionPropagation.descendants && !selectionPropagation.parents) {
    return newModel;
  }
  let shouldRegenerateModel = false;
  const newModelLookup = getLookupFromArray(newModel);
  const changes = getAddedAndRemovedItems({
    store,
    newModel,
    oldModel
  });
  additionalItemsToPropagate == null ? void 0 : additionalItemsToPropagate.forEach((itemId) => {
    if (newModelLookup[itemId]) {
      if (!changes.added.includes(itemId)) {
        changes.added.push(itemId);
      }
    } else if (!changes.removed.includes(itemId)) {
      changes.removed.push(itemId);
    }
  });
  changes.added.forEach((addedItemId) => {
    if (selectionPropagation.descendants) {
      const selectDescendants = (itemId) => {
        if (itemId !== addedItemId) {
          shouldRegenerateModel = true;
          newModelLookup[itemId] = true;
        }
        itemsSelectors.itemOrderedChildrenIds(store.state, itemId).forEach(selectDescendants);
      };
      selectDescendants(addedItemId);
    }
    if (selectionPropagation.parents) {
      const checkAllDescendantsSelected = (itemId) => {
        if (!newModelLookup[itemId]) {
          return false;
        }
        const children = itemsSelectors.itemOrderedChildrenIds(store.state, itemId);
        return children.every(checkAllDescendantsSelected);
      };
      const selectParents = (itemId) => {
        const parentId = itemsSelectors.itemParentId(store.state, itemId);
        if (parentId == null) {
          return;
        }
        const siblings = itemsSelectors.itemOrderedChildrenIds(store.state, parentId);
        if (siblings.every(checkAllDescendantsSelected)) {
          shouldRegenerateModel = true;
          newModelLookup[parentId] = true;
          selectParents(parentId);
        }
      };
      selectParents(addedItemId);
    }
  });
  changes.removed.forEach((removedItemId) => {
    if (selectionPropagation.parents) {
      let parentId = itemsSelectors.itemParentId(store.state, removedItemId);
      while (parentId != null) {
        if (newModelLookup[parentId]) {
          shouldRegenerateModel = true;
          delete newModelLookup[parentId];
        }
        parentId = itemsSelectors.itemParentId(store.state, parentId);
      }
    }
    if (selectionPropagation.descendants) {
      const deSelectDescendants = (itemId) => {
        if (itemId !== removedItemId) {
          shouldRegenerateModel = true;
          delete newModelLookup[itemId];
        }
        itemsSelectors.itemOrderedChildrenIds(store.state, itemId).forEach(deSelectDescendants);
      };
      deSelectDescendants(removedItemId);
    }
  });
  return shouldRegenerateModel ? Object.keys(newModelLookup) : newModel;
};

// node_modules/@mui/x-tree-view/esm/internals/plugins/useTreeViewSelection/useTreeViewSelection.itemPlugin.js
var selectorCheckboxSelectionStatus = createSelector((state, itemId) => {
  if (selectionSelectors.isItemSelected(state, itemId)) {
    return "checked";
  }
  let hasSelectedDescendant = false;
  let hasUnSelectedDescendant = false;
  const traverseDescendants = (itemToTraverseId) => {
    if (itemToTraverseId !== itemId) {
      if (selectionSelectors.isItemSelected(state, itemToTraverseId)) {
        hasSelectedDescendant = true;
      } else {
        hasUnSelectedDescendant = true;
      }
    }
    itemsSelectors.itemOrderedChildrenIds(state, itemToTraverseId).forEach(traverseDescendants);
  };
  traverseDescendants(itemId);
  const shouldSelectBasedOnDescendants = selectionSelectors.propagationRules(state).parents;
  if (shouldSelectBasedOnDescendants) {
    if (hasSelectedDescendant && hasUnSelectedDescendant) {
      return "indeterminate";
    }
    if (hasSelectedDescendant && !hasUnSelectedDescendant) {
      return "checked";
    }
    return "empty";
  }
  if (hasSelectedDescendant) {
    return "indeterminate";
  }
  return "empty";
});
var useTreeViewSelectionItemPlugin = ({
  props
}) => {
  const {
    itemId
  } = props;
  const {
    store
  } = useTreeViewContext();
  const isCheckboxSelectionEnabled = useStore(store, selectionSelectors.isCheckboxSelectionEnabled);
  const isItemSelectionEnabled = useStore(store, selectionSelectors.canItemBeSelected, itemId);
  const checkboxSelectionStatus = useStore(store, selectorCheckboxSelectionStatus, itemId);
  return {
    propsEnhancers: {
      checkbox: ({
        externalEventHandlers,
        interactions
      }) => {
        const handleChange = (event) => {
          var _a;
          (_a = externalEventHandlers.onChange) == null ? void 0 : _a.call(externalEventHandlers, event);
          if (event.defaultMuiPrevented) {
            return;
          }
          if (!selectionSelectors.canItemBeSelected(store.state, itemId)) {
            return;
          }
          interactions.handleCheckboxSelection(event);
        };
        return {
          tabIndex: -1,
          onChange: handleChange,
          visible: isCheckboxSelectionEnabled,
          disabled: !isItemSelectionEnabled,
          checked: checkboxSelectionStatus === "checked",
          indeterminate: checkboxSelectionStatus === "indeterminate"
        };
      }
    }
  };
};

// node_modules/@mui/x-tree-view/esm/internals/plugins/useTreeViewSelection/useTreeViewSelection.js
var useTreeViewSelection = ({
  store,
  params
}) => {
  useAssertModelConsistency({
    componentName: "Tree View",
    propName: "selectedItems",
    controlled: params.selectedItems,
    defaultValue: params.defaultSelectedItems
  });
  const lastSelectedItem = React11.useRef(null);
  const lastSelectedRange = React11.useRef({});
  const setSelectedItems = (event, newModel, additionalItemsToPropagate) => {
    var _a;
    const oldModel = selectionSelectors.selectedItemsRaw(store.state);
    let cleanModel;
    const isMultiSelectEnabled = selectionSelectors.isMultiSelectEnabled(store.state);
    if (isMultiSelectEnabled && (params.selectionPropagation.descendants || params.selectionPropagation.parents)) {
      cleanModel = propagateSelection({
        store,
        selectionPropagation: params.selectionPropagation,
        newModel,
        oldModel,
        additionalItemsToPropagate
      });
    } else {
      cleanModel = newModel;
    }
    if (params.onItemSelectionToggle) {
      if (isMultiSelectEnabled) {
        const changes = getAddedAndRemovedItems({
          store,
          newModel: cleanModel,
          oldModel
        });
        if (params.onItemSelectionToggle) {
          changes.added.forEach((itemId) => {
            params.onItemSelectionToggle(event, itemId, true);
          });
          changes.removed.forEach((itemId) => {
            params.onItemSelectionToggle(event, itemId, false);
          });
        }
      } else if (params.onItemSelectionToggle && cleanModel !== oldModel) {
        if (oldModel != null) {
          params.onItemSelectionToggle(event, oldModel, false);
        }
        if (cleanModel != null) {
          params.onItemSelectionToggle(event, cleanModel, true);
        }
      }
    }
    if (params.selectedItems === void 0) {
      store.set("selection", _extends({}, store.state.selection, {
        selectedItems: cleanModel
      }));
    }
    (_a = params.onSelectedItemsChange) == null ? void 0 : _a.call(params, event, cleanModel);
  };
  const setItemSelection = ({
    itemId,
    event = null,
    keepExistingSelection = false,
    shouldBeSelected
  }) => {
    if (!selectionSelectors.enabled(store.state)) {
      return;
    }
    let newSelected;
    const isMultiSelectEnabled = selectionSelectors.isMultiSelectEnabled(store.state);
    if (keepExistingSelection) {
      const oldSelected = selectionSelectors.selectedItems(store.state);
      const isSelectedBefore = selectionSelectors.isItemSelected(store.state, itemId);
      if (isSelectedBefore && (shouldBeSelected === false || shouldBeSelected == null)) {
        newSelected = oldSelected.filter((id) => id !== itemId);
      } else if (!isSelectedBefore && (shouldBeSelected === true || shouldBeSelected == null)) {
        newSelected = [itemId].concat(oldSelected);
      } else {
        newSelected = oldSelected;
      }
    } else {
      if (shouldBeSelected === false || shouldBeSelected == null && selectionSelectors.isItemSelected(store.state, itemId)) {
        newSelected = isMultiSelectEnabled ? [] : null;
      } else {
        newSelected = isMultiSelectEnabled ? [itemId] : itemId;
      }
    }
    setSelectedItems(
      event,
      newSelected,
      // If shouldBeSelected === selectionSelectors.isItemSelected(store, itemId), we still want to propagate the select.
      // This is useful when the element is in an indeterminate state.
      [itemId]
    );
    lastSelectedItem.current = itemId;
    lastSelectedRange.current = {};
  };
  const selectRange = (event, [start, end]) => {
    const isMultiSelectEnabled = selectionSelectors.isMultiSelectEnabled(store.state);
    if (!isMultiSelectEnabled) {
      return;
    }
    let newSelectedItems = selectionSelectors.selectedItems(store.state).slice();
    if (Object.keys(lastSelectedRange.current).length > 0) {
      newSelectedItems = newSelectedItems.filter((id) => !lastSelectedRange.current[id]);
    }
    const selectedItemsLookup = getLookupFromArray(newSelectedItems);
    const range = getNonDisabledItemsInRange(store.state, start, end);
    const itemsToAddToModel = range.filter((id) => !selectedItemsLookup[id]);
    newSelectedItems = newSelectedItems.concat(itemsToAddToModel);
    setSelectedItems(event, newSelectedItems);
    lastSelectedRange.current = getLookupFromArray(range);
  };
  const expandSelectionRange = (event, itemId) => {
    if (lastSelectedItem.current != null) {
      const [start, end] = findOrderInTremauxTree(store.state, itemId, lastSelectedItem.current);
      selectRange(event, [start, end]);
    }
  };
  const selectRangeFromStartToItem = (event, itemId) => {
    selectRange(event, [getFirstNavigableItem(store.state), itemId]);
  };
  const selectRangeFromItemToEnd = (event, itemId) => {
    selectRange(event, [itemId, getLastNavigableItem(store.state)]);
  };
  const selectAllNavigableItems = (event) => {
    const isMultiSelectEnabled = selectionSelectors.isMultiSelectEnabled(store.state);
    if (!isMultiSelectEnabled) {
      return;
    }
    const navigableItems = getAllNavigableItems(store.state);
    setSelectedItems(event, navigableItems);
    lastSelectedRange.current = getLookupFromArray(navigableItems);
  };
  const selectItemFromArrowNavigation = (event, currentItem, nextItem) => {
    const isMultiSelectEnabled = selectionSelectors.isMultiSelectEnabled(store.state);
    if (!isMultiSelectEnabled) {
      return;
    }
    let newSelectedItems = selectionSelectors.selectedItems(store.state).slice();
    if (Object.keys(lastSelectedRange.current).length === 0) {
      newSelectedItems.push(nextItem);
      lastSelectedRange.current = {
        [currentItem]: true,
        [nextItem]: true
      };
    } else {
      if (!lastSelectedRange.current[currentItem]) {
        lastSelectedRange.current = {};
      }
      if (lastSelectedRange.current[nextItem]) {
        newSelectedItems = newSelectedItems.filter((id) => id !== currentItem);
        delete lastSelectedRange.current[currentItem];
      } else {
        newSelectedItems.push(nextItem);
        lastSelectedRange.current[nextItem] = true;
      }
    }
    setSelectedItems(event, newSelectedItems);
  };
  useIsoLayoutEffect(() => {
    store.set("selection", {
      selectedItems: params.selectedItems === void 0 ? store.state.selection.selectedItems : params.selectedItems,
      isEnabled: !params.disableSelection,
      isMultiSelectEnabled: params.multiSelect,
      isCheckboxSelectionEnabled: params.checkboxSelection,
      selectionPropagation: {
        descendants: params.selectionPropagation.descendants,
        parents: params.selectionPropagation.parents
      }
    });
  }, [store, params.selectedItems, params.multiSelect, params.checkboxSelection, params.disableSelection, params.selectionPropagation.descendants, params.selectionPropagation.parents]);
  return {
    getRootProps: () => ({
      "aria-multiselectable": params.multiSelect
    }),
    publicAPI: {
      setItemSelection
    },
    instance: {
      setItemSelection,
      selectAllNavigableItems,
      expandSelectionRange,
      selectRangeFromStartToItem,
      selectRangeFromItemToEnd,
      selectItemFromArrowNavigation
    }
  };
};
useTreeViewSelection.itemPlugin = useTreeViewSelectionItemPlugin;
var DEFAULT_SELECTED_ITEMS = [];
var EMPTY_SELECTION_PROPAGATION = {};
useTreeViewSelection.applyDefaultValuesToParams = ({
  params
}) => _extends({}, params, {
  disableSelection: params.disableSelection ?? false,
  multiSelect: params.multiSelect ?? false,
  checkboxSelection: params.checkboxSelection ?? false,
  defaultSelectedItems: params.defaultSelectedItems ?? (params.multiSelect ? DEFAULT_SELECTED_ITEMS : null),
  selectionPropagation: params.selectionPropagation ?? EMPTY_SELECTION_PROPAGATION
});
useTreeViewSelection.getInitialState = (params) => ({
  selection: {
    selectedItems: params.selectedItems === void 0 ? params.defaultSelectedItems : params.selectedItems,
    isEnabled: !params.disableSelection,
    isMultiSelectEnabled: params.multiSelect,
    isCheckboxSelectionEnabled: params.checkboxSelection,
    selectionPropagation: params.selectionPropagation
  }
});
useTreeViewSelection.params = {
  disableSelection: true,
  multiSelect: true,
  checkboxSelection: true,
  defaultSelectedItems: true,
  selectedItems: true,
  onSelectedItemsChange: true,
  onItemSelectionToggle: true,
  selectionPropagation: true
};

// node_modules/@mui/x-tree-view/esm/internals/plugins/useTreeViewFocus/useTreeViewFocus.selectors.js
var defaultFocusableItemIdSelector = createSelectorMemoized(selectionSelectors.selectedItems, expansionSelectors.expandedItemsMap, itemsSelectors.itemMetaLookup, itemsSelectors.disabledItemFocusable, (state) => itemsSelectors.itemOrderedChildrenIds(state, null), (selectedItems, expandedItemsMap, itemMetaLookup, disabledItemsFocusable, orderedRootItemIds) => {
  const firstSelectedItem = selectedItems.find((itemId) => {
    if (!disabledItemsFocusable && isItemDisabled(itemMetaLookup, itemId)) {
      return false;
    }
    const itemMeta = itemMetaLookup[itemId];
    return itemMeta && (itemMeta.parentId == null || expandedItemsMap.has(itemMeta.parentId));
  });
  if (firstSelectedItem != null) {
    return firstSelectedItem;
  }
  const firstNavigableItem = orderedRootItemIds.find((itemId) => disabledItemsFocusable || !isItemDisabled(itemMetaLookup, itemId));
  if (firstNavigableItem != null) {
    return firstNavigableItem;
  }
  return null;
});
var focusSelectors = {
  /**
   * Gets the item that should be sequentially focusable (usually with the Tab key).
   * At any point in time, there is a single item that can be sequentially focused in the Tree View.
   * This item is the first selected item (that is both visible and navigable), if any, or the first navigable item if no item is selected.
   */
  defaultFocusableItemId: defaultFocusableItemIdSelector,
  /**
   * Checks whether an item is the default focusable item.
   */
  isItemTheDefaultFocusableItem: createSelector(defaultFocusableItemIdSelector, (defaultFocusableItemId, itemId) => defaultFocusableItemId === itemId),
  /**
   * Gets the id of the item that is currently focused.
   */
  focusedItemId: createSelector((state) => state.focus.focusedItemId),
  /**
   * Checks whether an item is focused.
   */
  isItemFocused: createSelector((state, itemId) => state.focus.focusedItemId === itemId)
};

// node_modules/@mui/x-tree-view/esm/internals/plugins/useTreeViewFocus/useTreeViewFocus.js
var useTreeViewFocus = ({
  instance,
  params,
  store
}) => {
  const setFocusedItemId = useEventCallback((itemId) => {
    const focusedItemId = focusSelectors.focusedItemId(store.state);
    if (focusedItemId === itemId) {
      return;
    }
    store.set("focus", _extends({}, store.state.focus, {
      focusedItemId: itemId
    }));
  });
  const isItemVisible = (itemId) => {
    const itemMeta = itemsSelectors.itemMeta(store.state, itemId);
    return itemMeta && (itemMeta.parentId == null || expansionSelectors.isItemExpanded(store.state, itemMeta.parentId));
  };
  const innerFocusItem = (event, itemId) => {
    const itemElement = instance.getItemDOMElement(itemId);
    if (itemElement) {
      itemElement.focus();
    }
    setFocusedItemId(itemId);
    if (params.onItemFocus) {
      params.onItemFocus(event, itemId);
    }
  };
  const focusItem = useEventCallback((event, itemId) => {
    if (isItemVisible(itemId)) {
      innerFocusItem(event, itemId);
    }
  });
  const removeFocusedItem = useEventCallback(() => {
    const focusedItemId = focusSelectors.focusedItemId(store.state);
    if (focusedItemId == null) {
      return;
    }
    const itemMeta = itemsSelectors.itemMeta(store.state, focusedItemId);
    if (itemMeta) {
      const itemElement = instance.getItemDOMElement(focusedItemId);
      if (itemElement) {
        itemElement.blur();
      }
    }
    setFocusedItemId(null);
  });
  useStoreEffect(store, itemsSelectors.itemMetaLookup, () => {
    const focusedItemId = focusSelectors.focusedItemId(store.state);
    if (focusedItemId == null) {
      return;
    }
    const hasItemBeenRemoved = !itemsSelectors.itemMeta(store.state, focusedItemId);
    if (!hasItemBeenRemoved) {
      return;
    }
    const defaultFocusableItemId = focusSelectors.defaultFocusableItemId(store.state);
    if (defaultFocusableItemId == null) {
      setFocusedItemId(null);
      return;
    }
    innerFocusItem(null, defaultFocusableItemId);
  });
  const createRootHandleFocus = (otherHandlers) => (event) => {
    var _a;
    (_a = otherHandlers.onFocus) == null ? void 0 : _a.call(otherHandlers, event);
    if (event.defaultMuiPrevented) {
      return;
    }
    const defaultFocusableItemId = focusSelectors.defaultFocusableItemId(store.state);
    if (event.target === event.currentTarget && defaultFocusableItemId != null) {
      innerFocusItem(event, defaultFocusableItemId);
    }
  };
  const createRootHandleBlur = (otherHandlers) => (event) => {
    var _a;
    (_a = otherHandlers.onBlur) == null ? void 0 : _a.call(otherHandlers, event);
    if (event.defaultMuiPrevented) {
      return;
    }
    setFocusedItemId(null);
  };
  return {
    getRootProps: (otherHandlers) => ({
      onFocus: createRootHandleFocus(otherHandlers),
      onBlur: createRootHandleBlur(otherHandlers)
    }),
    publicAPI: {
      focusItem
    },
    instance: {
      focusItem,
      removeFocusedItem
    }
  };
};
useTreeViewFocus.getInitialState = () => ({
  focus: {
    focusedItemId: null
  }
});
useTreeViewFocus.params = {
  onItemFocus: true
};

// node_modules/@mui/x-tree-view/esm/internals/plugins/useTreeViewLabel/useTreeViewLabel.itemPlugin.js
var React12 = __toESM(require_react(), 1);

// node_modules/@mui/x-tree-view/esm/internals/plugins/useTreeViewLabel/useTreeViewLabel.selectors.js
var labelSelectors = {
  /**
   * Checks whether an item is editable.
   */
  isItemEditable: createSelector((state) => {
    var _a;
    return (_a = state.label) == null ? void 0 : _a.isItemEditable;
  }, itemsSelectors.itemModel, (isItemEditable, itemModel, _itemId) => {
    if (!itemModel || isItemEditable == null) {
      return false;
    }
    if (typeof isItemEditable === "boolean") {
      return isItemEditable;
    }
    return isItemEditable(itemModel);
  }),
  /**
   * Checks whether an item is being edited.
   */
  isItemBeingEdited: createSelector((state, itemId) => {
    var _a;
    return itemId == null ? false : ((_a = state.label) == null ? void 0 : _a.editedItemId) === itemId;
  }),
  /**
   * Checks whether any item is being edited.
   */
  isAnyItemBeingEdited: createSelector((state) => {
    var _a;
    return !!((_a = state.label) == null ? void 0 : _a.editedItemId);
  })
};

// node_modules/@mui/x-tree-view/esm/internals/plugins/useTreeViewLabel/useTreeViewLabel.itemPlugin.js
var useTreeViewLabelItemPlugin = ({
  props
}) => {
  const {
    store
  } = useTreeViewContext();
  const {
    label,
    itemId
  } = props;
  const [labelInputValue, setLabelInputValue] = React12.useState(label);
  const isItemEditable = useStore(store, labelSelectors.isItemEditable, itemId);
  const isItemBeingEdited = useStore(store, labelSelectors.isItemBeingEdited, itemId);
  React12.useEffect(() => {
    if (!isItemBeingEdited) {
      setLabelInputValue(label);
    }
  }, [isItemBeingEdited, label]);
  return {
    propsEnhancers: {
      label: () => ({
        editable: isItemEditable
      }),
      labelInput: ({
        externalEventHandlers,
        interactions
      }) => {
        if (!isItemEditable) {
          return {};
        }
        const handleKeydown = (event) => {
          var _a;
          (_a = externalEventHandlers.onKeyDown) == null ? void 0 : _a.call(externalEventHandlers, event);
          if (event.defaultMuiPrevented) {
            return;
          }
          const target = event.target;
          if (event.key === "Enter" && target.value) {
            interactions.handleSaveItemLabel(event, target.value);
          } else if (event.key === "Escape") {
            interactions.handleCancelItemLabelEditing(event);
          }
        };
        const handleBlur = (event) => {
          var _a;
          (_a = externalEventHandlers.onBlur) == null ? void 0 : _a.call(externalEventHandlers, event);
          if (event.defaultMuiPrevented) {
            return;
          }
          if (event.target.value) {
            interactions.handleSaveItemLabel(event, event.target.value);
          }
        };
        const handleInputChange = (event) => {
          var _a;
          (_a = externalEventHandlers.onChange) == null ? void 0 : _a.call(externalEventHandlers, event);
          setLabelInputValue(event.target.value);
        };
        return {
          value: labelInputValue ?? "",
          "data-element": "labelInput",
          onChange: handleInputChange,
          onKeyDown: handleKeydown,
          onBlur: handleBlur,
          autoFocus: true,
          type: "text"
        };
      }
    }
  };
};

// node_modules/@mui/x-tree-view/esm/internals/plugins/useTreeViewLabel/useTreeViewLabel.js
var useTreeViewLabel = ({
  store,
  params
}) => {
  const setEditedItem = (editedItemId) => {
    if (editedItemId !== null) {
      const isEditable = labelSelectors.isItemEditable(store.state, editedItemId);
      if (!isEditable) {
        return;
      }
    }
    store.set("label", _extends({}, store.state.label, {
      editedItemId
    }));
  };
  const updateItemLabel = (itemId, label) => {
    if (!label) {
      throw new Error(["MUI X: The Tree View component requires all items to have a `label` property.", "The label of an item cannot be empty.", itemId].join("\n"));
    }
    const item = store.state.items.itemMetaLookup[itemId];
    if (item.label === label) {
      return;
    }
    store.set("items", _extends({}, store.state.items, {
      itemMetaLookup: _extends({}, store.state.items.itemMetaLookup, {
        [itemId]: _extends({}, item, {
          label
        })
      })
    }));
    if (params.onItemLabelChange) {
      params.onItemLabelChange(itemId, label);
    }
  };
  useIsoLayoutEffect(() => {
    store.set("label", _extends({}, store.state.label, {
      isItemEditable: params.isItemEditable
    }));
  }, [store, params.isItemEditable]);
  return {
    instance: {
      setEditedItem,
      updateItemLabel
    },
    publicAPI: {
      setEditedItem,
      updateItemLabel
    }
  };
};
useTreeViewLabel.itemPlugin = useTreeViewLabelItemPlugin;
useTreeViewLabel.applyDefaultValuesToParams = ({
  params
}) => _extends({}, params, {
  isItemEditable: params.isItemEditable ?? false
});
useTreeViewLabel.getInitialState = (params) => ({
  label: {
    isItemEditable: params.isItemEditable,
    editedItemId: null
  }
});
useTreeViewLabel.params = {
  onItemLabelChange: true,
  isItemEditable: true
};

// node_modules/@mui/x-tree-view/esm/internals/utils/plugins.js
var hasPlugin = (instance, plugin) => {
  const plugins = instance.getAvailablePlugins();
  return plugins.has(plugin);
};

// node_modules/@mui/x-tree-view/esm/internals/plugins/useTreeViewLazyLoading/useTreeViewLazyLoading.selectors.js
var lazyLoadingSelectors = {
  /**
   * Gets the data source used to lazy load items.
   */
  dataSource: createSelector((state) => {
    var _a;
    return (_a = state.lazyLoading) == null ? void 0 : _a.dataSource;
  }),
  /**
   * Checks whether an item is loading.
   */
  isItemLoading: createSelector((state, itemId) => {
    var _a;
    return ((_a = state.lazyLoading) == null ? void 0 : _a.dataSource.loading[itemId ?? TREE_VIEW_ROOT_PARENT_ID]) ?? false;
  }),
  /**
   * Checks whether an item has errors.
   */
  itemHasError: createSelector((state, itemId) => {
    var _a;
    return !!((_a = state.lazyLoading) == null ? void 0 : _a.dataSource.errors[itemId ?? TREE_VIEW_ROOT_PARENT_ID]);
  }),
  /**
   * Get an item error.
   */
  itemError: createSelector((state, itemId) => {
    var _a;
    return (_a = state.lazyLoading) == null ? void 0 : _a.dataSource.errors[itemId ?? TREE_VIEW_ROOT_PARENT_ID];
  })
};

// node_modules/@mui/x-tree-view/esm/hooks/useTreeItemUtils/useTreeItemUtils.js
var itemHasChildren = (reactChildren) => {
  if (Array.isArray(reactChildren)) {
    return reactChildren.length > 0 && reactChildren.some(itemHasChildren);
  }
  return Boolean(reactChildren);
};
var useTreeItemUtils = ({
  itemId,
  children
}) => {
  const {
    instance,
    store,
    publicAPI
  } = useTreeViewContext();
  const isItemExpandable = useStore(store, expansionSelectors.isItemExpandable, itemId);
  const isLoading = useStore(store, lazyLoadingSelectors.isItemLoading, itemId);
  const hasError = useStore(store, lazyLoadingSelectors.itemHasError, itemId);
  const isExpandable = itemHasChildren(children) || isItemExpandable;
  const isExpanded = useStore(store, expansionSelectors.isItemExpanded, itemId);
  const isFocused = useStore(store, focusSelectors.isItemFocused, itemId);
  const isSelected = useStore(store, selectionSelectors.isItemSelected, itemId);
  const isDisabled = useStore(store, itemsSelectors.isItemDisabled, itemId);
  const isEditing = useStore(store, labelSelectors.isItemBeingEdited, itemId);
  const isEditable = useStore(store, labelSelectors.isItemEditable, itemId);
  const status = {
    expandable: isExpandable,
    expanded: isExpanded,
    focused: isFocused,
    selected: isSelected,
    disabled: isDisabled,
    editing: isEditing,
    editable: isEditable,
    loading: isLoading,
    error: hasError
  };
  const handleExpansion = (event) => {
    if (status.disabled) {
      return;
    }
    if (!status.focused) {
      instance.focusItem(event, itemId);
    }
    const multiple = selectionSelectors.isMultiSelectEnabled(store.state) && (event.shiftKey || event.ctrlKey || event.metaKey);
    if (status.expandable && !(multiple && expansionSelectors.isItemExpanded(store.state, itemId))) {
      instance.setItemExpansion({
        event,
        itemId
      });
    }
  };
  const handleSelection = (event) => {
    if (status.disabled) {
      return;
    }
    if (!status.focused && !status.editing) {
      instance.focusItem(event, itemId);
    }
    const multiple = selectionSelectors.isMultiSelectEnabled(store.state) && (event.shiftKey || event.ctrlKey || event.metaKey);
    if (multiple) {
      if (event.shiftKey) {
        instance.expandSelectionRange(event, itemId);
      } else {
        instance.setItemSelection({
          event,
          itemId,
          keepExistingSelection: true
        });
      }
    } else {
      instance.setItemSelection({
        event,
        itemId,
        shouldBeSelected: true
      });
    }
  };
  const handleCheckboxSelection = (event) => {
    const hasShift = event.nativeEvent.shiftKey;
    const isMultiSelectEnabled = selectionSelectors.isMultiSelectEnabled(store.state);
    if (isMultiSelectEnabled && hasShift) {
      instance.expandSelectionRange(event, itemId);
    } else {
      instance.setItemSelection({
        event,
        itemId,
        keepExistingSelection: isMultiSelectEnabled,
        shouldBeSelected: event.target.checked
      });
    }
  };
  const toggleItemEditing = () => {
    if (!hasPlugin(instance, useTreeViewLabel)) {
      return;
    }
    if (isEditing) {
      instance.setEditedItem(null);
    } else {
      instance.setEditedItem(itemId);
    }
  };
  const handleSaveItemLabel = (event, newLabel) => {
    if (!hasPlugin(instance, useTreeViewLabel)) {
      return;
    }
    if (labelSelectors.isItemBeingEdited(store.state, itemId)) {
      instance.updateItemLabel(itemId, newLabel);
      toggleItemEditing();
      instance.focusItem(event, itemId);
    }
  };
  const handleCancelItemLabelEditing = (event) => {
    if (!hasPlugin(instance, useTreeViewLabel)) {
      return;
    }
    if (labelSelectors.isItemBeingEdited(store.state, itemId)) {
      toggleItemEditing();
      instance.focusItem(event, itemId);
    }
  };
  const interactions = {
    handleExpansion,
    handleSelection,
    handleCheckboxSelection,
    toggleItemEditing,
    handleSaveItemLabel,
    handleCancelItemLabelEditing
  };
  return {
    interactions,
    status,
    publicAPI
  };
};

export {
  warnOnce,
  createUseThemeProps,
  useRefWithInit,
  useStore,
  Store,
  useMergedRefs,
  idSelectors,
  generateTreeItemIdAttribute,
  useTreeViewId,
  useTreeViewContext,
  useTreeViewStyleContext,
  TreeViewProvider,
  useEventCallback,
  TREE_VIEW_ROOT_PARENT_ID,
  buildSiblingIndexes,
  TreeViewItemDepthContext,
  itemsSelectors,
  useTreeViewItems,
  useIsoLayoutEffect,
  expansionSelectors,
  useTreeViewExpansion,
  getPreviousNavigableItem,
  getNextNavigableItem,
  getLastNavigableItem,
  getFirstNavigableItem,
  isTargetInDescendants,
  selectionSelectors,
  useTreeViewSelection,
  focusSelectors,
  useTreeViewFocus,
  hasPlugin,
  labelSelectors,
  useTreeViewLabel,
  itemHasChildren,
  useTreeItemUtils
};
/*! Bundled license information:

use-sync-external-store/cjs/use-sync-external-store-shim/with-selector.development.js:
  (**
   * @license React
   * use-sync-external-store-shim/with-selector.development.js
   *
   * Copyright (c) Meta Platforms, Inc. and affiliates.
   *
   * This source code is licensed under the MIT license found in the
   * LICENSE file in the root directory of this source tree.
   *)
*/
//# sourceMappingURL=chunk-PPC63MCR.js.map
