import 'dart:io';
import 'package:flutter/foundation.dart';

class ApiConfig {
  // Production API URL - deployed to Azure
  static String get baseUrl {
    // Use Azure backend in production
    return 'https://aada-backend-app12345.azurewebsites.net';
    // Use localhost for local testing:
    // return 'http://localhost:8000';
  }

  // API endpoints
  static const String documentsUpload = '/documents/upload';
  static const String documentsUploadRegistration = '/documents/upload-registration';
  static const String documentsList = '/documents/list';
  static const String documentsGet = '/documents';
  static const String documentsDelete = '/documents';

  // Auth endpoints
  static const String authLogin = '/auth/login';
  static const String authRegister = '/auth/register';

  // Timeouts
  static const Duration connectTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);

  // File upload constraints
  static const int maxFileSize = 10 * 1024 * 1024; // 10MB
  static const Set<String> allowedExtensions = {
    '.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx'
  };
}