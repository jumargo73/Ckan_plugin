import { Component, signal, OnInit } from '@angular/core';
import { RouterOutlet,RouterLink } from '@angular/router';

// ESTO SE EJECUTA ANTES QUE LA CLASE
(function() {
  const originalError = console.error;
  console.error = (...args: any[]) => {
    const msg = args.join(' ');
    if (msg.includes("reading 'click'") || msg.includes("reading 'on'")) return;
    originalError.apply(console, args);
  };
})();

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet,RouterLink], 
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit {
  protected readonly title = signal('Buscador...');

  ngOnInit() {
    window.addEventListener('unhandledrejection', (event) => {
		const errorMsg = event.reason?.message || '';
		if (errorMsg.includes('click') || errorMsg.includes('on')) {
		  event.preventDefault(); 
		  event.stopPropagation();
		}
	});

	// También silenciamos errores síncronos comunes de CKAN
	window.addEventListener('error', (event) => {
		if (event.message.includes('click') || event.message.includes('on')) {
		  event.preventDefault();
		  event.stopPropagation();
		}
	  }, true);
	}  
}

