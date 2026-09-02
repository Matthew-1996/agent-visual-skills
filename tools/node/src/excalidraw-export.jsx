import { exportToBlob } from "@excalidraw/excalidraw";


const blobToDataUrl = (blob) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.addEventListener("load", () => resolve(reader.result), { once: true });
    reader.addEventListener("error", () => reject(reader.error), { once: true });
    reader.readAsDataURL(blob);
  });


window.AgentVisualExcalidraw = Object.freeze({
  async exportScene(scene) {
    const appState = {
      viewBackgroundColor: "#ffffff",
      exportBackground: true,
      exportWithDarkMode: false,
      ...scene.appState,
    };
    const exportPadding = Number.isFinite(appState.exportPadding)
      ? appState.exportPadding
      : 40;
    const blob = await exportToBlob({
      elements: scene.elements,
      appState,
      files: scene.files ?? {},
      exportPadding,
      mimeType: "image/png",
      getDimensions(width, height) {
        return { width, height, scale: 1 };
      },
    });
    if (!blob || blob.type !== "image/png") {
      throw new Error("Excalidraw did not return a PNG blob");
    }
    return blobToDataUrl(blob);
  },
});
