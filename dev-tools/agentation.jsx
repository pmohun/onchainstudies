import React from 'react';
import { createRoot } from 'react-dom/client';
import { Agentation } from 'agentation';
const host = document.createElement('div');
host.id = 'well-read-agentation';
document.body.append(host);
createRoot(host).render(<Agentation appName="Well Read" />);
