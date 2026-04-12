import { Component, OnInit, OnDestroy, NgZone, ChangeDetectorRef ,Injectable } from '@angular/core';
import { CommonModule,SlicePipe } from '@angular/common';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { forkJoin } from 'rxjs';


@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})

export class DashboardComponent implements OnInit		 {
	
	public query: string = '';
	public global = { datasets: 0, organizaciones: 0 , tematicas: 0,promedioRecursos: 0  }; // Estático (Panorama)
	public totales: any = { datasets: 0, organizaciones: 0, grupos: 0,huerfanos:0 };
	public estadisticaGrupos: any = { asociados: 0, sinAsociar: 0, porcentaje: 0 };
	public resultados: any[] = [];
	public resultadosBusqueda: any[] = [];	
	public cargando: boolean = false;
	private timeout: any;
	public formatosGrafico: any[] = [];
	public topGrupos: any[] = [];
	public topOrganizaciones : any[] = [];
	public recursosPorOrg: any[] = [];
	public total =0;
	
	
	private intervalo: any;
	private readonly API_BASE = '/api/3/action/package_search';
	private readonly CKAN_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJ0OFJHcGxncnBMQ0UwZnFQU0d6OW9OYm1mUWlDejY0YU14S0p5cXRkN0RrIiwiaWF0IjoxNzc1NTIwNTU2fQ.gacCfUh6iJ1B-V1twX36RObHxU7vZUZwTqrHA7jF9VE';
	stats: any = null; 
	
	public resultadosHuerfanos: any[] = []; // Usa una variable específica para no mezclar
    public viendoHuerfanos: boolean = false;
	
	constructor(private http: HttpClient,private zone: NgZone, private cdr: ChangeDetectorRef) {
		const win = (window as any);
		  if (win.jQuery && !win.jQuery.fn.click) {
			win.jQuery.fn.click = function(handler: any) {
			  return this.on('click', handler);
			};
		  }
		
	}
  
	public metricas = {
	  totalDatasets: 0,
	  totalRecursos: 0,
	  formatos: {} as any
	};
	
	public privacidad = {
	  publicos: 0,
	  privados: 0,
	  porcentajePublico: 0
	};
	
	ngOnInit() {
		this.obtenerMetricasGlobales();
		// 2. Ejecutamos el intervalo fuera de Angular para evitar conflictos con CKAN
		this.zone.runOutsideAngular(() => {
		    this.intervalo = setInterval(() => {
			  // 3. Volvemos a entrar a la zona solo para pedir los datos y refrescar
			  this.zone.run(() => {
				this.obtenerMetricasGlobales();
			  });
			}, 30000); // 30 segundos
		});
	}
	
	ngOnDestroy() {
	  if (this.intervalo) {
		clearInterval(this.intervalo);
	  }
	}

	// Función para procesar los resultados que ya traes de la API
	actualizarDashboard(resultadosBusqueda: any[]) {
	  this.metricas.totalDatasets = this.resultadosBusqueda.length;
	  this.metricas.totalRecursos = 0;
	  this.metricas.formatos = {};

	  this.resultados.forEach(ds => {
		this.metricas.totalRecursos += ds.num_resources || 0;
		
		// Contamos formatos para el futuro gráfico
		ds.resources?.forEach((res: any) => {
		  const fmt = res.format.toUpperCase();
		  this.metricas.formatos[fmt] = (this.metricas.formatos[fmt] || 0) + 1;
		});
	  });
	}
	
	obtenerMetricasGlobalesold() {
	  this.cargando = true;
	  const headers = new HttpHeaders({ 'Authorization': this.CKAN_TOKEN });

	  // Petición de Búsqueda General (Estadísticas)
	  const paramsSearch = new HttpParams()
		.set('q', '*:*')
		.set('include_private', 'true')
		.set('rows', '0') // <--- Cambiado a 0: Dashboard vuela porque no descarga datasets
		.set('facet', 'true')
		.set('facet.field', '["organization","groups","res_format","capacity"]');

	  // Petición específica para Huérfanos (La que hablamos antes)
	  const paramsHuerfanos = new HttpParams()
		.set('q', '*:*')
		.set('fq', '-groups:[* TO *]')
		.set('include_private', 'true')
		.set('rows', '0');

	  forkJoin({
		stats: this.http.get<any>(this.API_BASE, { headers, params: paramsSearch }),
		huerfanos: this.http.get<any>(this.API_BASE, { headers, params: paramsHuerfanos }),
		grupos: this.http.get<any>('/api/3/action/group_list'),
		orgs: this.http.get<any>('/api/3/action/organization_list')
	  }).subscribe({
		next: (data) => {
		  const res = data.stats;
		  if (res.success) {
			this.totales.datasets = res.result.count;
			this.totales.huerfanos = data.huerfanos.result.count; // <--- Dato real exacto

			// Procesar Facetas (Formatos y Orgs)
			this.prepararGraficoFormatos(res.result.search_facets.res_format?.items || []);
			this.prepararGraficoOrganizaciones(res.result.search_facets.organization?.items || []);

			// Visibilidad (Público/Privado)
			const cap = res.result.search_facets.capacity?.items || [];
			this.privacidad.privados = cap.find((i: any) => i.name === 'private')?.count || 0;
			this.privacidad.publicos = this.totales.datasets - this.privacidad.privados;
			this.privacidad.porcentajePublico = this.totales.datasets > 0 ? (this.privacidad.publicos / this.totales.datasets) * 100 : 0;
			
			
			// Procesar Salud de Grupos
			const itemsGrupos = res.result.search_facets.groups?.items || [];
			this.estadisticaGrupos.total = res.result.count;
			this.estadisticaGrupos.asociados = itemsGrupos.reduce((acc: number, item: any) => acc + item.count, 0);
			this.estadisticaGrupos.sinAsociar = this.estadisticaGrupos.total - this.estadisticaGrupos.asociados;
			this.estadisticaGrupos.porcentaje = this.totales.datasets > 0 ? (this.estadisticaGrupos.asociados / this.totales.datasets) * 100 : 0;
		  }

		  if (data.grupos.success) this.totales.tematicas = data.grupos.result.length;
		  if (data.orgs.success) this.totales.organizaciones = data.orgs.result.length;

		  this.cargando = false;
		  this.cdr.detectChanges();
		},
		error: (err) => {
		  console.error('Error en Dashboard:', err);
		  this.cargando = false;
		}
	  });
	}
	
	
	obtenerMetricasGlobales() {
	  this.cargando = true;
	  
	  // Ahora apuntamos a tu nuevo endpoint único
	  const url = '/api/3/action/dashboard_stats';
	  
	  // Ya no necesitas params complejos, el backend ya sabe qué contar
	  this.http.get<any>(url).subscribe({
		next: (response) => {
		  // Si tu backend devuelve el objeto directamente
		  if (response) {
			this.stats = response; // Aquí ya tienes huerfanos, privados, etc.
			
			this.totales.datasets=this.stats.total_datasets
			this.totales.tematicas=this.stats.total_grupos
			this.totales.organizaciones=this.stats.total_orgs
			
			this.privacidad.privados=this.stats.privados
			this.privacidad.publicos = this.totales.datasets - this.privacidad.privados;
			
			this.totales.huerfanos = this.stats.huerfanos
			
			// Si aún usas las funciones de gráficos, les pasas la data limpia
			if (this.stats.formatos_raw) {
			  this.prepararGraficoFormatos(this.stats.formatos_raw);
			}
		  }
		  this.cargando = false;
		  this.cdr.detectChanges();
		},
		error: (err) => {
		  console.error('Error al obtener métricas del dashboard:', err);
		  this.cargando = false;
		  this.cdr.detectChanges();
		}
	  });
	}
	
	
	
	prepararGraficoFormatos(formatosObj: any) {
	  // 1. Convertimos el objeto {"CSV": 2} en una lista [{display_name: 'CSV', count: 2}]
	  // Esto lo hace compatible con tu lógica anterior
	  const items = Object.entries(formatosObj).map(([key, value]) => ({
		display_name: key,
		count: value as number
	  }));

	  // 2. Calculamos el total (ahora .reduce sí funcionará porque 'items' es una lista)
	  const total = items.reduce((acc, item) => acc + item.count, 0);
	  
	  // 3. Mantenemos tu lógica original de mapeo y colores
	  this.formatosGrafico = items.map(item => ({
		nombre: item.display_name,
		cantidad: item.count,
		porcentaje: total > 0 ? (item.count / total) * 100 : 0,
		color: this.obtenerColorFormat(item.display_name)
	  }))
	  .sort((a, b) => b.cantidad - a.cantidad) // Ordenamos de mayor a menor
	  .slice(0, 5); // Tomamos los 5 principales
	}



	
	
	prepararGraficoFormatosold(items: any[]) {
	  // 1. Ordenamos por cantidad
	  const total = items.reduce((acc, item) => acc + item.count, 0);
	  
	  this.formatosGrafico = items.map(item => ({
		nombre: item.display_name,
		cantidad: item.count,
		porcentaje: (item.count / total) * 100,
		color: this.obtenerColorFormat(item.display_name)
	  })).slice(0, 5); // Tomamos los 5 principales
	}
	
	obtenerColorFormat(fmt: string) {
	  const colors: any = { 'CSV': '#2ecc71', 'PDF': '#e74c3c', 'JSON': '#f1c40f', 'XLS': '#3498db' };
	  return colors[fmt.toUpperCase()] || '#95a5a6';
	}
	
	// 2. La nueva (para comparar organizaciones)
	prepararGraficoOrganizaciones(items: any[]) {
	  // Calculamos el máximo para que la barra más larga sea el 100% visual
	  const maxVal = Math.max(...items.map(i => i.count)) || 1;
	  
	  this.recursosPorOrg = items.map(item => ({
		nombre: item.display_name,
		total: item.count,
		ancho: (item.count / maxVal) * 100
	  })).slice(0, 5);
	}
	
	// buscador.component.ts

	// Función para buscar específicamente los "huérfanos"
	verListadoHuerfanos() {
	  this.cargando = true;
	  this.viendoHuerfanos = true;
	  this.resultadosHuerfanos = []; // Limpieza inicial
	  
	  const headers = new HttpHeaders({
		'Authorization': this.CKAN_TOKEN
	  });
	  
	  const params = new HttpParams()
		.set('rows', '100') // Subimos a 100 para ver más huérfanos de un golpe
		.set('include_private', 'true')
		// El signo menos (-) es el "NOT" en Solr (el buscador de CKAN)
		.set('fq', '-groups:[* TO *]'); 

	  // Filtro fq de CKAN para "Sin Grupos"
	  //const url = `/api/3/action/package_search?rows=10&fq=-groups:[* TO *]&include_private=True`;
	    const url = this.API_BASE;

	  this.http.get<any>(url, { headers, params }).subscribe({
		next: (res) => {
		  if (res.success) {
			this.resultadosHuerfanos = res.result.results;
		  }
		  this.cargando = false;
		  this.cdr.detectChanges(); // <--- CRÍTICO para que el HTML despierte
		},
		error: () => {
		  this.cargando = false;
		  this.cdr.detectChanges();
		}
	  });
	}

}

