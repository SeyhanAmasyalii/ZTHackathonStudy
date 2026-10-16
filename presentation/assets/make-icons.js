// Sunumda kullanılan ikonları PNG'ye çevirir. Çalıştırma: node make-icons.js
const path = require("path");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");
const list = {
  eye: "FaEyeSlash", users: "FaUserFriends", unlink: "FaUnlink", bolt: "FaBolt", code: "FaCode",
  sync: "FaSyncAlt", shield: "FaShieldAlt", check: "FaCheckCircle", warn: "FaExclamationTriangle",
  route: "FaRoute", github: "FaGithub", globe: "FaGlobe", video: "FaVideo", quote: "FaQuoteLeft",
  headset: "FaHeadset", clip: "FaClipboardList", user: "FaUser",
};
(async () => {
  for (const [name, comp] of Object.entries(list)) {
    for (const [suffix, color] of [["w", "#FFFFFF"], ["r", "#E10514"], ["g", "#91969B"]]) {
      const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(fa[comp], { color, size: "256" }));
      await sharp(Buffer.from(svg)).png().toFile(path.join(__dirname, "icons", `${name}-${suffix}.png`));
    }
  }
  console.log("ok");
})();
