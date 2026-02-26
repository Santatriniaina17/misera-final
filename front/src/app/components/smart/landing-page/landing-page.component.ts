import { Component, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { Router } from '@angular/router';
import { Dialog } from '@angular/cdk/dialog';
import { AboutModalComponent } from '../about-modal/about-modal.component';

@Component({
  selector: 'app-landing-page',
  imports: [MatButtonModule, MatIconModule],
  templateUrl: './landing-page.component.html',
  styleUrl: './landing-page.component.scss',
})
export class LandingPageComponent {
  route = inject(Router);
  private dialog = inject(Dialog);

  goToTry() {
    this.route.navigate(['/upload']);
  }

  openModal() {
    this.dialog.open(AboutModalComponent);
  }
}
