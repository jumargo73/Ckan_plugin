import { Component,OnInit  } from '@angular/core';
import { ActivatedRoute,RouterLink } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { CommonModule,Location } from '@angular/common';


@Component({
  selector: 'app-detalle',
  standalone: true,
  imports: [ CommonModule],
  templateUrl: './detalle.html',
  styleUrl: './detalle.css',
})
export class DetalleComponent implements OnInit {
  dataset: any;
  cargando: boolean = true;

  constructor(private route: ActivatedRoute, private http: HttpClient,private location: Location) {}

  ngOnInit() {
    // 1. Capturamos el ID de la URL
    const id = this.route.snapshot.paramMap.get('id');
    
    // 2. Pedimos los datos completos a CKAN
    this.http.get<any>(`/api/3/action/package_show?id=${id}`)
      .subscribe(res => {
        this.dataset = res.result;
		this.cargando = false;
      });
  }
  
  irAtras(): void {
    this.location.back();
  }
}
