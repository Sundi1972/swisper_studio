import {
  Store,
  TREE_VIEW_ROOT_PARENT_ID,
  TreeViewItemDepthContext,
  TreeViewProvider,
  buildSiblingIndexes,
  createUseThemeProps,
  expansionSelectors,
  generateTreeItemIdAttribute,
  getFirstNavigableItem,
  getLastNavigableItem,
  getNextNavigableItem,
  getPreviousNavigableItem,
  hasPlugin,
  idSelectors,
  isTargetInDescendants,
  itemHasChildren,
  itemsSelectors,
  labelSelectors,
  selectionSelectors,
  useEventCallback,
  useIsoLayoutEffect,
  useMergedRefs,
  useRefWithInit,
  useStore,
  useTreeViewContext,
  useTreeViewExpansion,
  useTreeViewFocus,
  useTreeViewId,
  useTreeViewItems,
  useTreeViewLabel,
  useTreeViewSelection,
  warnOnce
} from "./chunk-PPC63MCR.js";
import "./chunk-ZAR7M645.js";
import {
  useSlotProps_default
} from "./chunk-JNEFEYMA.js";
import "./chunk-JBJOCPQO.js";
import "./chunk-GNM62ZLU.js";
import "./chunk-LUSCGVD7.js";
import {
  _objectWithoutPropertiesLoose
} from "./chunk-AVUONKA5.js";
import "./chunk-ZJAHPD5B.js";
import "./chunk-FSGOIAKX.js";
import {
  composeClasses,
  generateUtilityClass,
  generateUtilityClasses,
  require_prop_types,
  styled_default2 as styled_default,
  useRtl
} from "./chunk-EJ34WKIJ.js";
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
  __publicField,
  __toESM
} from "./chunk-WOOG5QLI.js";

// node_modules/@mui/x-tree-view/esm/SimpleTreeView/SimpleTreeView.js
var React9 = __toESM(require_react(), 1);
var import_prop_types2 = __toESM(require_prop_types(), 1);

// node_modules/@mui/x-tree-view/esm/SimpleTreeView/simpleTreeViewClasses.js
function getSimpleTreeViewUtilityClass(slot) {
  return generateUtilityClass("MuiSimpleTreeView", slot);
}
var simpleTreeViewClasses = generateUtilityClasses("MuiSimpleTreeView", ["root", "item", "itemContent", "itemGroupTransition", "itemIconContainer", "itemLabel", "itemCheckbox"]);

// node_modules/@mui/x-tree-view/esm/internals/useTreeView/useTreeView.js
var React4 = __toESM(require_react(), 1);

// node_modules/@mui/x-tree-view/esm/internals/corePlugins/useTreeViewInstanceEvents/useTreeViewInstanceEvents.js
var React = __toESM(require_react(), 1);

// node_modules/@mui/x-tree-view/node_modules/@mui/x-internals/esm/EventManager/EventManager.js
var EventManager = class {
  constructor() {
    __publicField(this, "maxListeners", 20);
    __publicField(this, "warnOnce", false);
    __publicField(this, "events", {});
  }
  on(eventName, listener, options = {}) {
    let collection = this.events[eventName];
    if (!collection) {
      collection = {
        highPriority: /* @__PURE__ */ new Map(),
        regular: /* @__PURE__ */ new Map()
      };
      this.events[eventName] = collection;
    }
    if (options.isFirst) {
      collection.highPriority.set(listener, true);
    } else {
      collection.regular.set(listener, true);
    }
    if (true) {
      const collectionSize = collection.highPriority.size + collection.regular.size;
      if (collectionSize > this.maxListeners && !this.warnOnce) {
        this.warnOnce = true;
        console.warn([`Possible EventEmitter memory leak detected. ${collectionSize} ${eventName} listeners added.`].join("\n"));
      }
    }
  }
  removeListener(eventName, listener) {
    if (this.events[eventName]) {
      this.events[eventName].regular.delete(listener);
      this.events[eventName].highPriority.delete(listener);
    }
  }
  removeAllListeners() {
    this.events = {};
  }
  emit(eventName, ...args) {
    const collection = this.events[eventName];
    if (!collection) {
      return;
    }
    const highPriorityListeners = Array.from(collection.highPriority.keys());
    const regularListeners = Array.from(collection.regular.keys());
    for (let i = highPriorityListeners.length - 1; i >= 0; i -= 1) {
      const listener = highPriorityListeners[i];
      if (collection.highPriority.has(listener)) {
        listener.apply(this, args);
      }
    }
    for (let i = 0; i < regularListeners.length; i += 1) {
      const listener = regularListeners[i];
      if (collection.regular.has(listener)) {
        listener.apply(this, args);
      }
    }
  }
  once(eventName, listener) {
    const that = this;
    this.on(eventName, function oneTimeListener(...args) {
      that.removeListener(eventName, oneTimeListener);
      listener.apply(that, args);
    });
  }
};

// node_modules/@mui/x-tree-view/esm/internals/corePlugins/useTreeViewInstanceEvents/useTreeViewInstanceEvents.js
var isSyntheticEvent = (event) => {
  return event.isPropagationStopped !== void 0;
};
var useTreeViewInstanceEvents = () => {
  const [eventManager] = React.useState(() => new EventManager());
  const publishEvent = React.useCallback((...args) => {
    const [name, params, event = {}] = args;
    event.defaultMuiPrevented = false;
    if (isSyntheticEvent(event) && event.isPropagationStopped()) {
      return;
    }
    eventManager.emit(name, params, event);
  }, [eventManager]);
  const subscribeEvent = React.useCallback((event, handler) => {
    eventManager.on(event, handler);
    return () => {
      eventManager.removeListener(event, handler);
    };
  }, [eventManager]);
  return {
    instance: {
      $$publishEvent: publishEvent,
      $$subscribeEvent: subscribeEvent
    }
  };
};
useTreeViewInstanceEvents.params = {};

// node_modules/@mui/x-tree-view/esm/internals/corePlugins/useTreeViewOptionalPlugins/useTreeViewOptionalPlugins.js
var useTreeViewOptionalPlugins = ({
  plugins
}) => {
  const pluginSet = new Set(plugins);
  const getAvailablePlugins = () => pluginSet;
  return {
    instance: {
      getAvailablePlugins
    }
  };
};
useTreeViewOptionalPlugins.params = {};

// node_modules/@mui/x-tree-view/esm/internals/corePlugins/corePlugins.js
var TREE_VIEW_CORE_PLUGINS = [useTreeViewInstanceEvents, useTreeViewOptionalPlugins, useTreeViewId];

// node_modules/@mui/x-tree-view/esm/internals/useTreeView/useExtractPluginParamsFromProps.js
var React2 = __toESM(require_react(), 1);
var _excluded = ["apiRef"];
var useExtractPluginParamsFromProps = (_ref) => {
  let {
    props: {
      apiRef
    },
    plugins
  } = _ref, props = _objectWithoutPropertiesLoose(_ref.props, _excluded);
  const paramsLookup = React2.useMemo(() => {
    const tempParamsLookup = {};
    plugins.forEach((plugin) => {
      Object.assign(tempParamsLookup, plugin.params);
    });
    return tempParamsLookup;
  }, [plugins]);
  const {
    forwardedProps,
    pluginParams
  } = React2.useMemo(() => {
    const tempPluginParams = {};
    const tempForwardedProps = {};
    Object.keys(props).forEach((propName) => {
      const prop = props[propName];
      if (paramsLookup[propName]) {
        tempPluginParams[propName] = prop;
      } else {
        tempForwardedProps[propName] = prop;
      }
    });
    const pluginParamsWithDefaults = plugins.reduce((acc, plugin) => {
      if (plugin.applyDefaultValuesToParams) {
        return plugin.applyDefaultValuesToParams({
          params: acc
        });
      }
      return acc;
    }, tempPluginParams);
    return {
      forwardedProps: tempForwardedProps,
      pluginParams: pluginParamsWithDefaults
    };
  }, [plugins, props, paramsLookup]);
  return {
    forwardedProps,
    pluginParams,
    apiRef
  };
};

// node_modules/@mui/x-tree-view/esm/internals/useTreeView/useTreeViewBuildContext.js
var React3 = __toESM(require_react(), 1);
var useTreeViewBuildContext = (parameters) => {
  const {
    plugins,
    instance,
    publicAPI,
    store,
    rootRef
  } = parameters;
  const runItemPlugins = React3.useCallback((itemPluginProps) => {
    let finalRootRef = null;
    let finalContentRef = null;
    const pluginPropEnhancers = [];
    const pluginPropEnhancersNames = {};
    plugins.forEach((plugin) => {
      if (!plugin.itemPlugin) {
        return;
      }
      const itemPluginResponse = plugin.itemPlugin({
        props: itemPluginProps,
        rootRef: finalRootRef,
        contentRef: finalContentRef
      });
      if (itemPluginResponse == null ? void 0 : itemPluginResponse.rootRef) {
        finalRootRef = itemPluginResponse.rootRef;
      }
      if (itemPluginResponse == null ? void 0 : itemPluginResponse.contentRef) {
        finalContentRef = itemPluginResponse.contentRef;
      }
      if (itemPluginResponse == null ? void 0 : itemPluginResponse.propsEnhancers) {
        pluginPropEnhancers.push(itemPluginResponse.propsEnhancers);
        Object.keys(itemPluginResponse.propsEnhancers).forEach((propsEnhancerName) => {
          pluginPropEnhancersNames[propsEnhancerName] = true;
        });
      }
    });
    const resolvePropsEnhancer = (currentSlotName) => (currentSlotParams) => {
      const enhancedProps = {};
      pluginPropEnhancers.forEach((propsEnhancersForCurrentPlugin) => {
        const propsEnhancerForCurrentPluginAndSlot = propsEnhancersForCurrentPlugin[currentSlotName];
        if (propsEnhancerForCurrentPluginAndSlot != null) {
          Object.assign(enhancedProps, propsEnhancerForCurrentPluginAndSlot(currentSlotParams));
        }
      });
      return enhancedProps;
    };
    const propsEnhancers = Object.fromEntries(Object.keys(pluginPropEnhancersNames).map((propEnhancerName) => [propEnhancerName, resolvePropsEnhancer(propEnhancerName)]));
    return {
      contentRef: finalContentRef,
      rootRef: finalRootRef,
      propsEnhancers
    };
  }, [plugins]);
  const wrapItem = React3.useCallback(({
    itemId,
    children,
    idAttribute
  }) => {
    let finalChildren = children;
    for (let i = plugins.length - 1; i >= 0; i -= 1) {
      const plugin = plugins[i];
      if (plugin.wrapItem) {
        finalChildren = plugin.wrapItem({
          instance,
          itemId,
          children: finalChildren,
          idAttribute
        });
      }
    }
    return finalChildren;
  }, [plugins, instance]);
  const wrapRoot = React3.useCallback(({
    children
  }) => {
    let finalChildren = children;
    for (let i = plugins.length - 1; i >= 0; i -= 1) {
      const plugin = plugins[i];
      if (plugin.wrapRoot) {
        finalChildren = plugin.wrapRoot({
          children: finalChildren
        });
      }
    }
    return finalChildren;
  }, [plugins]);
  return React3.useMemo(() => ({
    runItemPlugins,
    wrapItem,
    wrapRoot,
    instance,
    publicAPI,
    store,
    rootRef
  }), [runItemPlugins, wrapItem, wrapRoot, instance, publicAPI, store, rootRef]);
};

// node_modules/@mui/x-tree-view/esm/internals/useTreeView/useTreeView.js
function initializeInputApiRef(inputApiRef) {
  if (inputApiRef.current == null) {
    inputApiRef.current = {};
  }
  return inputApiRef;
}
function useTreeViewApiInitialization(inputApiRef) {
  const fallbackPublicApiRef = React4.useRef({});
  if (inputApiRef) {
    return initializeInputApiRef(inputApiRef);
  }
  return fallbackPublicApiRef;
}
var useTreeView = ({
  plugins: inPlugins,
  rootRef,
  props
}) => {
  const plugins = React4.useMemo(() => [...TREE_VIEW_CORE_PLUGINS, ...inPlugins], [inPlugins]);
  const {
    pluginParams,
    forwardedProps,
    apiRef
  } = useExtractPluginParamsFromProps({
    plugins,
    props
  });
  const instance = useRefWithInit(() => ({})).current;
  const publicAPI = useTreeViewApiInitialization(apiRef);
  const innerRootRef = React4.useRef(null);
  const handleRootRef = useMergedRefs(innerRootRef, rootRef);
  const store = useRefWithInit(() => {
    const initialState = {};
    for (const plugin of plugins) {
      if (plugin.getInitialState) {
        Object.assign(initialState, plugin.getInitialState(pluginParams));
      }
    }
    return new Store(initialState);
  }).current;
  const contextValue = useTreeViewBuildContext({
    plugins,
    instance,
    publicAPI: publicAPI.current,
    store,
    rootRef: innerRootRef
  });
  const rootPropsGetters = [];
  const runPlugin = (plugin) => {
    const pluginResponse = plugin({
      instance,
      params: pluginParams,
      rootRef: innerRootRef,
      plugins,
      store
    });
    if (pluginResponse.getRootProps) {
      rootPropsGetters.push(pluginResponse.getRootProps);
    }
    if (pluginResponse.publicAPI) {
      Object.assign(publicAPI.current, pluginResponse.publicAPI);
    }
    if (pluginResponse.instance) {
      Object.assign(instance, pluginResponse.instance);
    }
  };
  plugins.forEach(runPlugin);
  const getRootProps = (otherHandlers = {}) => {
    const rootProps = _extends({
      role: "tree"
    }, forwardedProps, otherHandlers, {
      ref: handleRootRef
    });
    rootPropsGetters.forEach((rootPropsGetter) => {
      Object.assign(rootProps, rootPropsGetter(otherHandlers));
    });
    return rootProps;
  };
  return {
    getRootProps,
    rootRef: handleRootRef,
    contextValue
  };
};

// node_modules/@mui/x-tree-view/esm/internals/plugins/useTreeViewKeyboardNavigation/useTreeViewKeyboardNavigation.js
var React6 = __toESM(require_react(), 1);

// node_modules/@base-ui-components/utils/esm/useOnMount.js
var React5 = __toESM(require_react(), 1);
var EMPTY = [];
function useOnMount(fn) {
  React5.useEffect(fn, EMPTY);
}

// node_modules/@base-ui-components/utils/esm/useTimeout.js
var EMPTY2 = 0;
var Timeout = class _Timeout {
  constructor() {
    __publicField(this, "currentId", /* @__PURE__ */ (() => EMPTY2)());
    __publicField(this, "clear", () => {
      if (this.currentId !== EMPTY2) {
        clearTimeout(this.currentId);
        this.currentId = EMPTY2;
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
      this.currentId = EMPTY2;
      fn();
    }, delay);
  }
  isStarted() {
    return this.currentId !== EMPTY2;
  }
};
function useTimeout() {
  const timeout = useRefWithInit(Timeout.create).current;
  useOnMount(timeout.disposeEffect);
  return timeout;
}

// node_modules/@mui/x-tree-view/esm/internals/plugins/useTreeViewKeyboardNavigation/useTreeViewKeyboardNavigation.js
function isPrintableKey(string) {
  return !!string && string.length === 1 && !!string.match(/\S/);
}
var TYPEAHEAD_TIMEOUT = 500;
var useTreeViewKeyboardNavigation = ({
  instance,
  store,
  params
}) => {
  const isRtl = useRtl();
  const labelMap = React6.useRef({});
  const typeaheadQueryRef = React6.useRef("");
  const typeaheadTimeout = useTimeout();
  const updateLabelMap = useEventCallback((callback) => {
    labelMap.current = callback(labelMap.current);
  });
  const itemMetaLookup = useStore(store, itemsSelectors.itemMetaLookup);
  React6.useEffect(() => {
    if (instance.areItemUpdatesPrevented()) {
      return;
    }
    const newLabelMap = {};
    const processItem = (item) => {
      newLabelMap[item.id] = item.label.toLowerCase();
    };
    Object.values(itemMetaLookup).forEach(processItem);
    labelMap.current = newLabelMap;
  }, [itemMetaLookup, params.getItemId, instance]);
  const getNextItem = (itemIdToCheck) => {
    const nextItemId = getNextNavigableItem(store.state, itemIdToCheck);
    if (nextItemId === null) {
      return getFirstNavigableItem(store.state);
    }
    return nextItemId;
  };
  const getNextMatchingItemId = (itemId, query) => {
    let matchingItemId = null;
    const checkedItems = {};
    let currentItemId = query.length > 1 ? itemId : getNextItem(itemId);
    while (matchingItemId == null && !checkedItems[currentItemId]) {
      const itemLabel = labelMap.current[currentItemId];
      if (itemLabel == null ? void 0 : itemLabel.startsWith(query)) {
        matchingItemId = currentItemId;
      } else {
        checkedItems[currentItemId] = true;
        currentItemId = getNextItem(currentItemId);
      }
    }
    return matchingItemId;
  };
  const getFirstMatchingItem = (itemId, newKey) => {
    const cleanNewKey = newKey.toLowerCase();
    const concatenatedQuery = `${typeaheadQueryRef.current}${cleanNewKey}`;
    const concatenatedQueryMatchingItemId = getNextMatchingItemId(itemId, concatenatedQuery);
    if (concatenatedQueryMatchingItemId != null) {
      typeaheadQueryRef.current = concatenatedQuery;
      return concatenatedQueryMatchingItemId;
    }
    const newKeyMatchingItemId = getNextMatchingItemId(itemId, cleanNewKey);
    if (newKeyMatchingItemId != null) {
      typeaheadQueryRef.current = cleanNewKey;
      return newKeyMatchingItemId;
    }
    typeaheadQueryRef.current = "";
    return null;
  };
  const canToggleItemSelection = (itemId) => selectionSelectors.enabled(store.state) && !itemsSelectors.isItemDisabled(store.state, itemId);
  const canToggleItemExpansion = (itemId) => {
    return !itemsSelectors.isItemDisabled(store.state, itemId) && expansionSelectors.isItemExpandable(store.state, itemId);
  };
  const handleItemKeyDown = async (event, itemId) => {
    if (event.defaultMuiPrevented) {
      return;
    }
    if (event.altKey || isTargetInDescendants(event.target, event.currentTarget)) {
      return;
    }
    const ctrlPressed = event.ctrlKey || event.metaKey;
    const key = event.key;
    const isMultiSelectEnabled = selectionSelectors.isMultiSelectEnabled(store.state);
    switch (true) {
      case (key === " " && canToggleItemSelection(itemId)): {
        event.preventDefault();
        if (isMultiSelectEnabled && event.shiftKey) {
          instance.expandSelectionRange(event, itemId);
        } else {
          instance.setItemSelection({
            event,
            itemId,
            keepExistingSelection: isMultiSelectEnabled,
            shouldBeSelected: void 0
          });
        }
        break;
      }
      case key === "Enter": {
        if (hasPlugin(instance, useTreeViewLabel) && labelSelectors.isItemEditable(store.state, itemId) && !labelSelectors.isItemBeingEdited(store.state, itemId)) {
          instance.setEditedItem(itemId);
        } else if (canToggleItemExpansion(itemId)) {
          instance.setItemExpansion({
            event,
            itemId
          });
          event.preventDefault();
        } else if (canToggleItemSelection(itemId)) {
          if (isMultiSelectEnabled) {
            event.preventDefault();
            instance.setItemSelection({
              event,
              itemId,
              keepExistingSelection: true
            });
          } else if (!selectionSelectors.isItemSelected(store.state, itemId)) {
            instance.setItemSelection({
              event,
              itemId
            });
            event.preventDefault();
          }
        }
        break;
      }
      case key === "ArrowDown": {
        const nextItem = getNextNavigableItem(store.state, itemId);
        if (nextItem) {
          event.preventDefault();
          instance.focusItem(event, nextItem);
          if (isMultiSelectEnabled && event.shiftKey && canToggleItemSelection(nextItem)) {
            instance.selectItemFromArrowNavigation(event, itemId, nextItem);
          }
        }
        break;
      }
      case key === "ArrowUp": {
        const previousItem = getPreviousNavigableItem(store.state, itemId);
        if (previousItem) {
          event.preventDefault();
          instance.focusItem(event, previousItem);
          if (isMultiSelectEnabled && event.shiftKey && canToggleItemSelection(previousItem)) {
            instance.selectItemFromArrowNavigation(event, itemId, previousItem);
          }
        }
        break;
      }
      case (key === "ArrowRight" && !isRtl || key === "ArrowLeft" && isRtl): {
        if (ctrlPressed) {
          return;
        }
        if (expansionSelectors.isItemExpanded(store.state, itemId)) {
          const nextItemId = getNextNavigableItem(store.state, itemId);
          if (nextItemId) {
            instance.focusItem(event, nextItemId);
            event.preventDefault();
          }
        } else if (canToggleItemExpansion(itemId)) {
          instance.setItemExpansion({
            event,
            itemId
          });
          event.preventDefault();
        }
        break;
      }
      case (key === "ArrowLeft" && !isRtl || key === "ArrowRight" && isRtl): {
        if (ctrlPressed) {
          return;
        }
        if (canToggleItemExpansion(itemId) && expansionSelectors.isItemExpanded(store.state, itemId)) {
          instance.setItemExpansion({
            event,
            itemId
          });
          event.preventDefault();
        } else {
          const parent = itemsSelectors.itemParentId(store.state, itemId);
          if (parent) {
            instance.focusItem(event, parent);
            event.preventDefault();
          }
        }
        break;
      }
      case key === "Home": {
        if (canToggleItemSelection(itemId) && isMultiSelectEnabled && ctrlPressed && event.shiftKey) {
          instance.selectRangeFromStartToItem(event, itemId);
        } else {
          instance.focusItem(event, getFirstNavigableItem(store.state));
        }
        event.preventDefault();
        break;
      }
      case key === "End": {
        if (canToggleItemSelection(itemId) && isMultiSelectEnabled && ctrlPressed && event.shiftKey) {
          instance.selectRangeFromItemToEnd(event, itemId);
        } else {
          instance.focusItem(event, getLastNavigableItem(store.state));
        }
        event.preventDefault();
        break;
      }
      case key === "*": {
        instance.expandAllSiblings(event, itemId);
        event.preventDefault();
        break;
      }
      case (String.fromCharCode(event.keyCode) === "A" && ctrlPressed && isMultiSelectEnabled && selectionSelectors.enabled(store.state)): {
        instance.selectAllNavigableItems(event);
        event.preventDefault();
        break;
      }
      case (!ctrlPressed && !event.shiftKey && isPrintableKey(key)): {
        typeaheadTimeout.clear();
        const matchingItem = getFirstMatchingItem(itemId, key);
        if (matchingItem != null) {
          instance.focusItem(event, matchingItem);
          event.preventDefault();
        } else {
          typeaheadQueryRef.current = "";
        }
        typeaheadTimeout.start(TYPEAHEAD_TIMEOUT, () => {
          typeaheadQueryRef.current = "";
        });
        break;
      }
    }
  };
  return {
    instance: {
      updateLabelMap,
      handleItemKeyDown
    }
  };
};
useTreeViewKeyboardNavigation.params = {};

// node_modules/@mui/x-tree-view/esm/internals/plugins/useTreeViewJSXItems/useTreeViewJSXItems.js
var React8 = __toESM(require_react(), 1);

// node_modules/@mui/x-tree-view/esm/internals/TreeViewProvider/TreeViewChildrenItemProvider.js
var React7 = __toESM(require_react(), 1);
var import_prop_types = __toESM(require_prop_types(), 1);

// node_modules/@mui/x-tree-view/esm/internals/utils/utils.js
function escapeOperandAttributeSelector(operand) {
  return operand.replace(/["\\]/g, "\\$&");
}

// node_modules/@mui/x-tree-view/esm/internals/TreeViewProvider/TreeViewChildrenItemProvider.js
var import_jsx_runtime = __toESM(require_jsx_runtime(), 1);
var TreeViewChildrenItemContext = React7.createContext(null);
if (true) TreeViewChildrenItemContext.displayName = "TreeViewChildrenItemContext";
function TreeViewChildrenItemProvider(props) {
  const {
    children,
    itemId = null,
    idAttribute
  } = props;
  const {
    instance,
    store,
    rootRef
  } = useTreeViewContext();
  const childrenIdAttrToIdRef = React7.useRef(/* @__PURE__ */ new Map());
  React7.useEffect(() => {
    if (!rootRef.current) {
      return;
    }
    const previousChildrenIds = itemsSelectors.itemOrderedChildrenIds(store.state, itemId ?? null) ?? [];
    const escapedIdAttr = escapeOperandAttributeSelector(idAttribute ?? rootRef.current.id);
    if (itemId != null) {
      const itemRoot = rootRef.current.querySelector(`*[id="${escapedIdAttr}"][role="treeitem"]`);
      if (itemRoot && itemRoot.getAttribute("aria-expanded") === "false") {
        return;
      }
    }
    const childrenElements = rootRef.current.querySelectorAll(`${itemId == null ? "" : `*[id="${escapedIdAttr}"] `}[role="treeitem"]:not(*[id="${escapedIdAttr}"] [role="treeitem"] [role="treeitem"])`);
    const childrenIds = Array.from(childrenElements).map((child) => childrenIdAttrToIdRef.current.get(child.id));
    const hasChanged = childrenIds.length !== previousChildrenIds.length || childrenIds.some((childId, index) => childId !== previousChildrenIds[index]);
    if (hasChanged) {
      instance.setJSXItemsOrderedChildrenIds(itemId ?? null, childrenIds);
    }
  });
  const value = React7.useMemo(() => ({
    registerChild: (childIdAttribute, childItemId) => childrenIdAttrToIdRef.current.set(childIdAttribute, childItemId),
    unregisterChild: (childIdAttribute) => childrenIdAttrToIdRef.current.delete(childIdAttribute),
    parentId: itemId
  }), [itemId]);
  return (0, import_jsx_runtime.jsx)(TreeViewChildrenItemContext.Provider, {
    value,
    children
  });
}
true ? TreeViewChildrenItemProvider.propTypes = {
  children: import_prop_types.default.node,
  id: import_prop_types.default.string
} : void 0;

// node_modules/@mui/x-tree-view/esm/internals/plugins/useTreeViewJSXItems/useTreeViewJSXItems.js
var import_jsx_runtime2 = __toESM(require_jsx_runtime(), 1);
var useTreeViewJSXItems = ({
  instance,
  store
}) => {
  instance.preventItemUpdates();
  const insertJSXItem = useEventCallback((item) => {
    if (store.state.items.itemMetaLookup[item.id] != null) {
      throw new Error(["MUI X: The Tree View component requires all items to have a unique `id` property.", "Alternatively, you can use the `getItemId` prop to specify a custom id for each item.", `Two items were provided with the same id in the \`items\` prop: "${item.id}"`].join("\n"));
    }
    store.set("items", _extends({}, store.state.items, {
      itemMetaLookup: _extends({}, store.state.items.itemMetaLookup, {
        [item.id]: item
      }),
      // For Simple Tree View, we don't have a proper `item` object, so we create a very basic one.
      itemModelLookup: _extends({}, store.state.items.itemModelLookup, {
        [item.id]: {
          id: item.id,
          label: item.label ?? ""
        }
      })
    }));
    return () => {
      const newItemMetaLookup = _extends({}, store.state.items.itemMetaLookup);
      const newItemModelLookup = _extends({}, store.state.items.itemModelLookup);
      delete newItemMetaLookup[item.id];
      delete newItemModelLookup[item.id];
      store.set("items", _extends({}, store.state.items, {
        itemMetaLookup: newItemMetaLookup,
        itemModelLookup: newItemModelLookup
      }));
    };
  });
  const setJSXItemsOrderedChildrenIds = (parentId, orderedChildrenIds) => {
    const parentIdWithDefault = parentId ?? TREE_VIEW_ROOT_PARENT_ID;
    store.set("items", _extends({}, store.state.items, {
      itemOrderedChildrenIdsLookup: _extends({}, store.state.items.itemOrderedChildrenIdsLookup, {
        [parentIdWithDefault]: orderedChildrenIds
      }),
      itemChildrenIndexesLookup: _extends({}, store.state.items.itemChildrenIndexesLookup, {
        [parentIdWithDefault]: buildSiblingIndexes(orderedChildrenIds)
      })
    }));
  };
  const mapLabelFromJSX = useEventCallback((itemId, label) => {
    instance.updateLabelMap((labelMap) => {
      labelMap[itemId] = label;
      return labelMap;
    });
    return () => {
      instance.updateLabelMap((labelMap) => {
        const newMap = _extends({}, labelMap);
        delete newMap[itemId];
        return newMap;
      });
    };
  });
  return {
    instance: {
      insertJSXItem,
      setJSXItemsOrderedChildrenIds,
      mapLabelFromJSX
    }
  };
};
var useTreeViewJSXItemsItemPlugin = ({
  props,
  rootRef,
  contentRef
}) => {
  const {
    instance,
    store
  } = useTreeViewContext();
  const {
    children,
    disabled = false,
    label,
    itemId,
    id
  } = props;
  const parentContext = React8.useContext(TreeViewChildrenItemContext);
  if (parentContext == null) {
    throw new Error(["MUI X: Could not find the Tree View Children Item context.", "It looks like you rendered your component outside of a SimpleTreeView parent component.", "This can also happen if you are bundling multiple versions of the Tree View."].join("\n"));
  }
  const {
    registerChild,
    unregisterChild,
    parentId
  } = parentContext;
  const expandable = itemHasChildren(children);
  const pluginContentRef = React8.useRef(null);
  const handleContentRef = useMergedRefs(pluginContentRef, contentRef);
  const treeId = useStore(store, idSelectors.treeId);
  useIsoLayoutEffect(() => {
    const idAttribute = generateTreeItemIdAttribute({
      itemId,
      treeId,
      id
    });
    registerChild(idAttribute, itemId);
    return () => {
      unregisterChild(idAttribute);
      unregisterChild(idAttribute);
    };
  }, [store, instance, registerChild, unregisterChild, itemId, id, treeId]);
  useIsoLayoutEffect(() => {
    return instance.insertJSXItem({
      id: itemId,
      idAttribute: id,
      parentId,
      expandable,
      disabled
    });
  }, [instance, parentId, itemId, expandable, disabled, id]);
  React8.useEffect(() => {
    var _a;
    if (label) {
      return instance.mapLabelFromJSX(itemId, (((_a = pluginContentRef.current) == null ? void 0 : _a.textContent) ?? "").toLowerCase());
    }
    return void 0;
  }, [instance, itemId, label]);
  return {
    contentRef: handleContentRef,
    rootRef
  };
};
useTreeViewJSXItems.itemPlugin = useTreeViewJSXItemsItemPlugin;
useTreeViewJSXItems.wrapItem = ({
  children,
  itemId,
  idAttribute
}) => {
  const depthContext = React8.useContext(TreeViewItemDepthContext);
  return (0, import_jsx_runtime2.jsx)(TreeViewChildrenItemProvider, {
    itemId,
    idAttribute,
    children: (0, import_jsx_runtime2.jsx)(TreeViewItemDepthContext.Provider, {
      value: depthContext + 1,
      children
    })
  });
};
if (true) useTreeViewJSXItems.wrapItem.displayName = "useTreeViewJSXItems.wrapItem";
useTreeViewJSXItems.wrapRoot = ({
  children
}) => (0, import_jsx_runtime2.jsx)(TreeViewChildrenItemProvider, {
  itemId: null,
  idAttribute: null,
  children: (0, import_jsx_runtime2.jsx)(TreeViewItemDepthContext.Provider, {
    value: 0,
    children
  })
});
if (true) useTreeViewJSXItems.wrapRoot.displayName = "useTreeViewJSXItems.wrapRoot";
useTreeViewJSXItems.params = {};

// node_modules/@mui/x-tree-view/esm/SimpleTreeView/SimpleTreeView.plugins.js
var SIMPLE_TREE_VIEW_PLUGINS = [useTreeViewItems, useTreeViewExpansion, useTreeViewSelection, useTreeViewFocus, useTreeViewKeyboardNavigation, useTreeViewJSXItems];

// node_modules/@mui/x-tree-view/esm/SimpleTreeView/SimpleTreeView.js
var import_jsx_runtime3 = __toESM(require_jsx_runtime(), 1);
var _excluded2 = ["slots", "slotProps"];
var useThemeProps = createUseThemeProps("MuiSimpleTreeView");
var useUtilityClasses = (ownerState) => {
  const {
    classes
  } = ownerState;
  return React9.useMemo(() => {
    const slots = {
      root: ["root"],
      item: ["item"],
      itemContent: ["itemContent"],
      itemGroupTransition: ["itemGroupTransition"],
      itemIconContainer: ["itemIconContainer"],
      itemLabel: ["itemLabel"],
      // itemLabelInput: ['itemLabelInput'], => feature not available on this component
      itemCheckbox: ["itemCheckbox"]
      // itemDragAndDropOverlay: ['itemDragAndDropOverlay'], => feature not available on this component
      // itemErrorIcon: ['itemErrorIcon'], => feature not available on this component
    };
    return composeClasses(slots, getSimpleTreeViewUtilityClass, classes);
  }, [classes]);
};
var SimpleTreeViewRoot = styled_default("ul", {
  name: "MuiSimpleTreeView",
  slot: "Root"
})({
  padding: 0,
  margin: 0,
  listStyle: "none",
  outline: 0,
  position: "relative"
});
var EMPTY_ITEMS = [];
var SimpleTreeView = React9.forwardRef(function SimpleTreeView2(inProps, ref) {
  const props = useThemeProps({
    props: inProps,
    name: "MuiSimpleTreeView"
  });
  const {
    slots,
    slotProps
  } = props, other = _objectWithoutPropertiesLoose(props, _excluded2);
  if (true) {
    if (props.items != null) {
      warnOnce(["MUI X: The Simple Tree View component does not support the `items` prop.", "If you want to add items, you need to pass them as JSX children.", "Check the documentation for more details: https://mui.com/x/react-tree-view/simple-tree-view/items/."]);
    }
  }
  const {
    getRootProps,
    contextValue
  } = useTreeView({
    plugins: SIMPLE_TREE_VIEW_PLUGINS,
    rootRef: ref,
    props: _extends({}, other, {
      items: EMPTY_ITEMS
    })
  });
  const classes = useUtilityClasses(props);
  const Root = (slots == null ? void 0 : slots.root) ?? SimpleTreeViewRoot;
  const rootProps = useSlotProps_default({
    elementType: Root,
    externalSlotProps: slotProps == null ? void 0 : slotProps.root,
    className: classes.root,
    getSlotProps: getRootProps,
    ownerState: props
  });
  return (0, import_jsx_runtime3.jsx)(TreeViewProvider, {
    contextValue,
    classes,
    slots,
    slotProps,
    children: (0, import_jsx_runtime3.jsx)(Root, _extends({}, rootProps))
  });
});
if (true) SimpleTreeView.displayName = "SimpleTreeView";
true ? SimpleTreeView.propTypes = {
  // ----------------------------- Warning --------------------------------
  // | These PropTypes are generated from the TypeScript type definitions |
  // | To update them edit the TypeScript types and run "pnpm proptypes"  |
  // ----------------------------------------------------------------------
  /**
   * The ref object that allows Tree View manipulation. Can be instantiated with `useTreeViewApiRef()`.
   */
  apiRef: import_prop_types2.default.shape({
    current: import_prop_types2.default.shape({
      focusItem: import_prop_types2.default.func,
      getItem: import_prop_types2.default.func,
      getItemDOMElement: import_prop_types2.default.func,
      getItemOrderedChildrenIds: import_prop_types2.default.func,
      getItemTree: import_prop_types2.default.func,
      getParentId: import_prop_types2.default.func,
      isItemExpanded: import_prop_types2.default.func,
      setIsItemDisabled: import_prop_types2.default.func,
      setItemExpansion: import_prop_types2.default.func,
      setItemSelection: import_prop_types2.default.func
    })
  }),
  /**
   * If `true`, the Tree View renders a checkbox at the left of its label that allows selecting it.
   * @default false
   */
  checkboxSelection: import_prop_types2.default.bool,
  /**
   * The content of the component.
   */
  children: import_prop_types2.default.node,
  /**
   * Override or extend the styles applied to the component.
   */
  classes: import_prop_types2.default.object,
  className: import_prop_types2.default.string,
  /**
   * Expanded item ids.
   * Used when the item's expansion is not controlled.
   * @default []
   */
  defaultExpandedItems: import_prop_types2.default.arrayOf(import_prop_types2.default.string),
  /**
   * Selected item ids. (Uncontrolled)
   * When `multiSelect` is true this takes an array of strings; when false (default) a string.
   * @default []
   */
  defaultSelectedItems: import_prop_types2.default.any,
  /**
   * If `true`, will allow focus on disabled items.
   * @default false
   */
  disabledItemsFocusable: import_prop_types2.default.bool,
  /**
   * If `true` selection is disabled.
   * @default false
   */
  disableSelection: import_prop_types2.default.bool,
  /**
   * Expanded item ids.
   * Used when the item's expansion is controlled.
   */
  expandedItems: import_prop_types2.default.arrayOf(import_prop_types2.default.string),
  /**
   * The slot that triggers the item's expansion when clicked.
   * @default 'content'
   */
  expansionTrigger: import_prop_types2.default.oneOf(["content", "iconContainer"]),
  /**
   * This prop is used to help implement the accessibility logic.
   * If you don't provide this prop. It falls back to a randomly generated id.
   */
  id: import_prop_types2.default.string,
  /**
   * Horizontal indentation between an item and its children.
   * Examples: 24, "24px", "2rem", "2em".
   * @default 12px
   */
  itemChildrenIndentation: import_prop_types2.default.oneOfType([import_prop_types2.default.number, import_prop_types2.default.string]),
  /**
   * If `true`, `ctrl` and `shift` will trigger multiselect.
   * @default false
   */
  multiSelect: import_prop_types2.default.bool,
  /**
   * Callback fired when Tree Items are expanded/collapsed.
   * @param {React.SyntheticEvent} event The DOM event that triggered the change. Can be null when the change is caused by the `publicAPI.setItemExpansion()` method.
   * @param {array} itemIds The ids of the expanded items.
   */
  onExpandedItemsChange: import_prop_types2.default.func,
  /**
   * Callback fired when the `content` slot of a given Tree Item is clicked.
   * @param {React.MouseEvent} event The DOM event that triggered the change.
   * @param {string} itemId The id of the focused item.
   */
  onItemClick: import_prop_types2.default.func,
  /**
   * Callback fired when a Tree Item is expanded or collapsed.
   * @param {React.SyntheticEvent | null} event The DOM event that triggered the change. Can be null when the change is caused by the `publicAPI.setItemExpansion()` method.
   * @param {array} itemId The itemId of the modified item.
   * @param {boolean} isExpanded `true` if the item has just been expanded, `false` if it has just been collapsed.
   */
  onItemExpansionToggle: import_prop_types2.default.func,
  /**
   * Callback fired when a given Tree Item is focused.
   * @param {React.SyntheticEvent | null} event The DOM event that triggered the change. **Warning**: This is a generic event not a focus event.
   * @param {string} itemId The id of the focused item.
   */
  onItemFocus: import_prop_types2.default.func,
  /**
   * Callback fired when a Tree Item is selected or deselected.
   * @param {React.SyntheticEvent} event The DOM event that triggered the change. Can be null when the change is caused by the `publicAPI.setItemSelection()` method.
   * @param {array} itemId The itemId of the modified item.
   * @param {boolean} isSelected `true` if the item has just been selected, `false` if it has just been deselected.
   */
  onItemSelectionToggle: import_prop_types2.default.func,
  /**
   * Callback fired when Tree Items are selected/deselected.
   * @param {React.SyntheticEvent} event The DOM event that triggered the change. Can be null when the change is caused by the `publicAPI.setItemSelection()` method.
   * @param {string[] | string} itemIds The ids of the selected items.
   * When `multiSelect` is `true`, this is an array of strings; when false (default) a string.
   */
  onSelectedItemsChange: import_prop_types2.default.func,
  /**
   * Selected item ids. (Controlled)
   * When `multiSelect` is true this takes an array of strings; when false (default) a string.
   */
  selectedItems: import_prop_types2.default.any,
  /**
   * When `selectionPropagation.descendants` is set to `true`.
   *
   * - Selecting a parent selects all its descendants automatically.
   * - Deselecting a parent deselects all its descendants automatically.
   *
   * When `selectionPropagation.parents` is set to `true`.
   *
   * - Selecting all the descendants of a parent selects the parent automatically.
   * - Deselecting a descendant of a selected parent deselects the parent automatically.
   *
   * Only works when `multiSelect` is `true`.
   * On the <SimpleTreeView />, only the expanded items are considered (since the collapsed item are not passed to the Tree View component at all)
   *
   * @default { parents: false, descendants: false }
   */
  selectionPropagation: import_prop_types2.default.shape({
    descendants: import_prop_types2.default.bool,
    parents: import_prop_types2.default.bool
  }),
  /**
   * The props used for each component slot.
   */
  slotProps: import_prop_types2.default.object,
  /**
   * Overridable component slots.
   */
  slots: import_prop_types2.default.object,
  /**
   * The system prop that allows defining system overrides as well as additional CSS styles.
   */
  sx: import_prop_types2.default.oneOfType([import_prop_types2.default.arrayOf(import_prop_types2.default.oneOfType([import_prop_types2.default.func, import_prop_types2.default.object, import_prop_types2.default.bool])), import_prop_types2.default.func, import_prop_types2.default.object])
} : void 0;
export {
  SimpleTreeView,
  SimpleTreeViewRoot,
  getSimpleTreeViewUtilityClass,
  simpleTreeViewClasses
};
//# sourceMappingURL=@mui_x-tree-view_SimpleTreeView.js.map
