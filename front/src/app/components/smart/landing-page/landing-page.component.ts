import { Component, inject, OnInit } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { Router } from '@angular/router';
import { Dialog } from '@angular/cdk/dialog';
import { AboutModalComponent } from '../about-modal/about-modal.component';
import { PredictionService } from '../../../services/prediction.service';

@Component({
  selector: 'app-landing-page',
  imports: [MatButtonModule, MatIconModule],
  templateUrl: './landing-page.component.html',
  styleUrl: './landing-page.component.scss',
})
export class LandingPageComponent implements OnInit {
  route = inject(Router);
  private dialog = inject(Dialog);
  constructor(private predictionService: PredictionService) {}

  ngOnInit(): void {
    // Ping backend dès le chargement
    this.predictionService.ping().subscribe((res) => {
      console.log('Backend réveillé !', res);
    });
  }
  goToTry() {
    this.route.navigate(['/upload']);
  }

  openModal() {
    this.dialog.open(AboutModalComponent);
  }
}
