import { Component,OnInit,ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute,RouterLink  } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { Subject, of } from 'rxjs';
import { debounceTime, distinctUntilChanged, switchMap, tap, catchError, filter } from 'rxjs/operators';



@Component({
  selector: 'app-buscador',
  standalone: true,
  imports: [CommonModule, FormsModule], // Necesarios para *ngIf, *ngFor y ngModel
  templateUrl: './buscador.html',
  styleUrl: './buscador.css'
})

export class BuscadorComponent implements OnInit{
  public query: string = '';
  private buscador$ = new Subject<string>();
  public resultados: any[] = [];
  public cargando: boolean = false;
  private timeout: any;

  constructor(private http: HttpClient,private cdr: ChangeDetectorRef) {}
  
 ngOnInit() {
	  this.buscador$.pipe(
		// 1. Solo actúa si hay 3 o más caracteres
		tap(term => {
		  if (term.length < 3) {
			this.resultados = [];
			this.cargando = false;
			this.cdr.detectChanges();
		  }
		}),
		filter(term => term.length >= 3),

		// 2. Reemplaza tu setTimeout (400ms de espera)
		debounceTime(400),

		// 3. No busques si el texto es igual al anterior
		distinctUntilChanged(),

		// 4. Indica que empezó la carga
		tap(() => {
		  this.cargando = true;
		  this.cdr.detectChanges();
		}),

		// 5. LA MAGIA: switchMap cancela la petición anterior si llega una nueva
		switchMap(term => {
		  const url = `/api/3/action/package_search?q=${term}`;
		  return this.http.get<any>(url).pipe(
			catchError(err => {
			  console.error('Error en CKAN', err);
			  return of({ success: false, result: { results: [] } });
			})
		  );
		})
	  ).subscribe(response => {
		if (response.success) {
		  this.resultados = response.result.results;
		}
		this.cargando = false;
		this.cdr.detectChanges();
	  });
	}

	// Tu función en el HTML ahora solo hace esto:
	ejecutarBusqueda() {
	  this.buscador$.next(this.query);
	}
  
}

