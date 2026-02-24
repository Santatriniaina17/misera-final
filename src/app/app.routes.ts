import { Routes } from '@angular/router';
import { LandingPageComponent } from './components/smart/landing-page/landing-page.component';
import { UploadPageComponent } from './components/smart/upload-page/upload-page.component';

export const routes: Routes = [
  { path: 'landing', component: LandingPageComponent },
  { path: 'upload', component: UploadPageComponent },
  { path: '', redirectTo: 'landing', pathMatch: 'full' },
];
