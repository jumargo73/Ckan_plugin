import { Routes } from '@angular/router';
import { BuscadorComponent } from './buscador/buscador';
import { DetalleComponent } from './detalle/detalle'; 
import { DashboardComponent  } from './dashboard/dashboard'; 
// Si creas otro componente, lo importas aquí:
// import { GraficaComponent } from './grafica/grafica'; 

export const routes: Routes = [
  // Si la URL es la home de CKAN
  { path: 'buscar', component: BuscadorComponent },
  { path: 'detalle', component: DetalleComponent }, 
  { path: 'dashboard', component: DashboardComponent },
  { path: '', component: BuscadorComponent, pathMatch: 'full' } 
];

