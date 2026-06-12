const { getDefaultConfig } = require("expo/metro-config");
const { withNativeWind } = require("nativewind/metro");
const path = require("path");

const config = getDefaultConfig(__dirname);

// Web platform: alias react-native to react-native-web and mock native-only modules
const originalResolveRequest = config.resolver.resolveRequest;

config.resolver.resolveRequest = (context, moduleName, platform) => {
  if (platform === "web") {
    // Redirect react-native to react-native-web
    if (moduleName === "react-native" || moduleName.startsWith("react-native/Libraries/")) {
      // For deep imports into react-native internals, return empty module
      if (moduleName.startsWith("react-native/Libraries/")) {
        return {
          type: "empty",
        };
      }
      return context.resolveRequest(context, "react-native-web", platform);
    }

    // Mock react-native-maps for web
    if (moduleName === "react-native-maps" || moduleName.startsWith("react-native-maps/")) {
      return {
        type: "empty",
      };
    }
  }

  if (originalResolveRequest) {
    return originalResolveRequest(context, moduleName, platform);
  }
  return context.resolveRequest(context, moduleName, platform);
};

module.exports = withNativeWind(config, { input: "./global.css" });
