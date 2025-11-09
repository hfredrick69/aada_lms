# Page snapshot

```yaml
- generic [ref=e3]:
  - generic [ref=e4]: "[plugin:vite:import-analysis] Failed to resolve import \"react-signature-canvas\" from \"src/pages/PublicSign.tsx\". Does the file exist?"
  - generic [ref=e5]: /app/src/pages/PublicSign.tsx:3:28
  - generic [ref=e6]: "3 | import { useState, useEffect, useRef } from \"react\"; 4 | import { useParams, useNavigate } from \"react-router-dom\"; 5 | import SignatureCanvas from \"react-signature-canvas\"; | ^ 6 | import axios from \"axios\"; 7 | const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || \"http://localhost:8000/api\";"
  - generic [ref=e7]: at TransformPluginContext._formatLog (file:///app/node_modules/vite/dist/node/chunks/config.js:31106:43) at TransformPluginContext.error (file:///app/node_modules/vite/dist/node/chunks/config.js:31103:14) at normalizeUrl (file:///app/node_modules/vite/dist/node/chunks/config.js:29590:18) at process.processTicksAndRejections (node:internal/process/task_queues:95:5) at async file:///app/node_modules/vite/dist/node/chunks/config.js:29648:32 at async Promise.all (index 3) at async TransformPluginContext.transform (file:///app/node_modules/vite/dist/node/chunks/config.js:29616:4) at async EnvironmentPluginContainer.transform (file:///app/node_modules/vite/dist/node/chunks/config.js:30905:14) at async loadAndTransform (file:///app/node_modules/vite/dist/node/chunks/config.js:26043:26) at async viteTransformMiddleware (file:///app/node_modules/vite/dist/node/chunks/config.js:27118:20)
  - generic [ref=e8]:
    - text: Click outside, press Esc key, or fix the code to dismiss.
    - text: You can also disable this overlay by setting
    - code [ref=e9]: server.hmr.overlay
    - text: to
    - code [ref=e10]: "false"
    - text: in
    - code [ref=e11]: vite.config.ts
    - text: .
```