import { Component, inject } from '@angular/core';
import { Dialog, DialogModule } from '@angular/cdk/dialog';

@Component({
  selector: 'app-about-modal',
  imports: [DialogModule],
  templateUrl: './about-modal.component.html',
  styleUrl: './about-modal.component.scss',
})
export class AboutModalComponent {
  private dialog = inject(Dialog);

  close() {
    this.dialog.closeAll();
  }
}
