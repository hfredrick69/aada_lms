import 'dart:convert';
import 'package:dio/dio.dart';
import '../models/user.dart';
import '../utils/secure_storage.dart';

class AuthService {
  static const String baseUrl = 'https://aada-backend-app12345.azurewebsites.net'; // Azure production URL
  // For local testing, use: 'http://127.0.0.1:8000'
  late final Dio _dio;

  AuthService() {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      headers: {'Content-Type': 'application/json'},
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
    ));

    // Add interceptor to automatically add auth token
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        // Don't add token for login, register, or refresh endpoints
        if (!options.path.contains('/auth/login') &&
            !options.path.contains('/auth/register') &&
            !options.path.contains('/auth/refresh')) {
          final token = await SecureStorage.getAccessToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
        }
        handler.next(options);
      },
      onError: (error, handler) async {
        // Auto-refresh token on 401 errors (but not for login/register/refresh endpoints)
        if (error.response?.statusCode == 401 &&
            !error.requestOptions.path.contains('/auth/login') &&
            !error.requestOptions.path.contains('/auth/register') &&
            !error.requestOptions.path.contains('/auth/refresh')) {
          final refreshed = await _refreshToken();
          if (refreshed) {
            // Retry the original request
            final token = await SecureStorage.getAccessToken();
            error.requestOptions.headers['Authorization'] = 'Bearer $token';
            final response = await _dio.fetch(error.requestOptions);
            return handler.resolve(response);
          } else {
            // Refresh failed, logout user
            await logout();
          }
        }
        handler.next(error);
      },
    ));
  }

  // Register new user
  Future<Map<String, dynamic>?> register(RegisterRequest request) async {
    try {
      print('🔵 Registering user at: $baseUrl/auth/register');
      print('🔵 Request payload: ${request.toJson()}');
      final response = await _dio.post('/auth/register', data: request.toJson());
      print('🔵 Response: ${response.data}');
      return response.data;
    } on DioException catch (e) {
      print('❌ Registration error: ${e.response?.data ?? e.message}');
      print('❌ Status code: ${e.response?.statusCode}');
      print('❌ Full response: ${e.response}');
      throw _handleError(e);
    }
  }

  // Login user
  Future<AuthResponse?> login(LoginRequest request) async {
    try {
      final response = await _dio.post('/auth/login', data: request.toJson());
      final authResponse = AuthResponse.fromJson(response.data);

      // Store tokens securely
      await SecureStorage.setAccessToken(authResponse.accessToken);
      await SecureStorage.setRefreshToken(authResponse.refreshToken);
      await SecureStorage.setUserData(json.encode(authResponse.user.toJson()));

      return authResponse;
    } on DioException catch (e) {
      print('Login error: ${e.response?.data ?? e.message}');
      throw _handleError(e);
    }
  }

  // Refresh access token
  Future<bool> _refreshToken() async {
    try {
      final refreshToken = await SecureStorage.getRefreshToken();
      if (refreshToken == null) return false;

      final response = await _dio.post('/auth/refresh', data: {
        'refresh_token': refreshToken,
      });

      final newAccessToken = response.data['access_token'];
      await SecureStorage.setAccessToken(newAccessToken);
      return true;
    } catch (e) {
      print('Token refresh error: $e');
      return false;
    }
  }

  // Get current user info
  Future<User?> getCurrentUser() async {
    try {
      final response = await _dio.get('/auth/me');
      return User.fromJson(response.data);
    } on DioException catch (e) {
      print('Get user error: ${e.response?.data ?? e.message}');
      return null;
    }
  }

  // Verify email
  Future<bool> verifyEmail(String token) async {
    try {
      await _dio.post('/auth/verify-email', data: {'token': token});
      return true;
    } on DioException catch (e) {
      print('Email verification error: ${e.response?.data ?? e.message}');
      return false;
    }
  }

  // Request password reset
  Future<bool> forgotPassword(String email) async {
    try {
      await _dio.post('/auth/forgot-password', data: {'email': email});
      return true;
    } on DioException catch (e) {
      print('Forgot password error: ${e.response?.data ?? e.message}');
      return false;
    }
  }

  // Reset password
  Future<bool> resetPassword(String token, String newPassword) async {
    try {
      await _dio.post('/auth/reset-password', data: {
        'token': token,
        'new_password': newPassword,
      });
      return true;
    } on DioException catch (e) {
      print('Reset password error: ${e.response?.data ?? e.message}');
      return false;
    }
  }

  // Logout user
  Future<void> logout() async {
    await SecureStorage.clearAll();
  }

  // Check if user is logged in
  Future<bool> isLoggedIn() async {
    return await SecureStorage.isLoggedIn();
  }

  // Get stored user data
  Future<User?> getStoredUser() async {
    try {
      final userData = await SecureStorage.getUserData();
      if (userData != null) {
        return User.fromJson(json.decode(userData));
      }
      return null;
    } catch (e) {
      print('Error getting stored user: $e');
      return null;
    }
  }

  // Handle Dio errors and convert to user-friendly messages
  String _handleError(DioException error) {
    if (error.response != null) {
      final data = error.response!.data;
      if (data is Map<String, dynamic> && data.containsKey('detail')) {
        return data['detail'];
      }
      return 'Server error: ${error.response!.statusCode}';
    } else if (error.type == DioExceptionType.connectionTimeout ||
               error.type == DioExceptionType.receiveTimeout) {
      return 'Connection timeout. Please check your internet connection.';
    } else if (error.type == DioExceptionType.connectionError) {
      return 'Unable to connect to server. Please try again later.';
    }
    return 'An unexpected error occurred. Please try again.';
  }
}