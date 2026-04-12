import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { App } from './app/app';

document.addEventListener('DOMContentLoaded', () => {
  // 1. Verifica si el elemento de tu App existe en el HTML actual
  const rootElement = document.querySelector('app-root'); 

  // 3. SOLO arranca si el elemento existe en esta página
  if (rootElement) {
    bootstrapApplication(App, appConfig)
      .catch((err) => {
        // Solo logueamos errores reales de la aplicación
        console.error('Error al arrancar Angular:', err);
      });
  } 
});
