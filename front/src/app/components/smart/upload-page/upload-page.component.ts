import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDividerModule } from '@angular/material/divider';
import { FormsModule } from '@angular/forms';
import { ResultsComponent } from '../../ui/results/results.component';
import { PredictionResult, SellerType } from '../../../models/prediction.model';
import { HttpErrorResponse } from '@angular/common/http';
import { PredictionService } from '../../../services/prediction.service';

@Component({
  selector: 'app-upload-page',
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatButtonToggleModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatDividerModule,
    ResultsComponent,
  ],
  templateUrl: './upload-page.component.html',
  styleUrl: './upload-page.component.scss',
})
export class UploadPageComponent {
  selectedType = signal<SellerType | null>(null);
  selectedFile = signal<File | null>(null);
  isLoading = signal(false);
  isDragging = signal(false);
  result = signal<PredictionResult | null>(null);

  constructor(
    private predictionService: PredictionService,
    private snackBar: MatSnackBar,
  ) {}

  get canSubmit(): () => boolean {
    return () => !!(this.selectedType() && this.selectedFile());
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files?.[0]) this.selectedFile.set(input.files[0]);
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
    this.isDragging.set(true);
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    this.isDragging.set(false);
    const file = event.dataTransfer?.files[0];
    if (file && file.name.endsWith('.csv')) this.selectedFile.set(file);
    else
      this.snackBar.open('Veuillez déposer un fichier .csv', 'OK', {
        duration: 3000,
      });
  }

  submit() {
    if (!this.selectedFile() || !this.selectedType()) return;
    this.isLoading.set(true);
    this.predictionService
      .predict(this.selectedFile()!, this.selectedType()!)
      .subscribe({
        next: (res: PredictionResult) => {
          this.result.set(res);
          this.isLoading.set(false);
        },
        error: (err: HttpErrorResponse) => {
          const msg = err.error?.error || 'Erreur lors de la prédiction';
          this.snackBar.open(msg, 'Fermer', {
            duration: 5000,
            panelClass: 'error-snack',
          });
          this.isLoading.set(false);
        },
      });
  }

  reset() {
    this.result.set(null);
    this.selectedFile.set(null);
  }
}
