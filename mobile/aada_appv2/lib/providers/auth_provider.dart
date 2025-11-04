import 'package:flutter/foundation.dart';
import '../models/user.dart';
import '../services/auth_service.dart';

enum AuthStatus { initial, loading, authenticated, unauthenticated }

class AuthProvider with ChangeNotifier {
  final AuthService _authService = AuthService();

  AuthStatus _status = AuthStatus.initial;
  User? _user;
  String? _errorMessage;

  AuthStatus get status => _status;
  User? get user => _user;
  String? get errorMessage => _errorMessage;
  bool get isAuthenticated => _status == AuthStatus.authenticated && _user != null;
  bool get isLoading => _status == AuthStatus.loading;

  // Initialize auth state
  Future<void> initialize() async {
    _setLoading();

    try {
      final isLoggedIn = await _authService.isLoggedIn();
      if (isLoggedIn) {
        // Try to get stored user data first
        _user = await _authService.getStoredUser();

        // If stored data exists, mark as authenticated
        if (_user != null) {
          _status = AuthStatus.authenticated;
          notifyListeners();

          // Try to refresh user data in background
          _refreshUserData();
        } else {
          // No stored user data, need to login again
          await logout();
        }
      } else {
        _status = AuthStatus.unauthenticated;
        notifyListeners();
      }
    } catch (e) {
      print('Auth initialization error: $e');
      _status = AuthStatus.unauthenticated;
      notifyListeners();
    }
  }

  // Register new user
  Future<Map<String, dynamic>?> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
  }) async {
    _setLoading();

    try {
      final request = RegisterRequest(
        email: email,
        password: password,
        firstName: firstName,
        lastName: lastName,
      );

      final result = await _authService.register(request);

      if (result != null) {
        _status = AuthStatus.unauthenticated;
        _errorMessage = null;
        notifyListeners();
        return result; // Return the full registration response
      }
      return null;
    } catch (e) {
      _setError(e.toString());
      return null;
    }
  }

  // Login user
  Future<bool> login({required String email, required String password}) async {
    _setLoading();

    try {
      final request = LoginRequest(email: email, password: password);
      print('🔐 Attempting login for: $email');
      final authResponse = await _authService.login(request);

      if (authResponse != null) {
        print('✅ Login successful! User: ${authResponse.user.email}');
        _user = authResponse.user;
        _status = AuthStatus.authenticated;
        _errorMessage = null;
        notifyListeners();
        print('📢 State updated - Status: $_status, User: ${_user?.email}');
        return true;
      }
      print('❌ Login failed - no auth response');
      return false;
    } catch (e) {
      print('❌ Login error: $e');
      _setError(e.toString());
      return false;
    }
  }

  // Logout user
  Future<void> logout() async {
    await _authService.logout();
    _user = null;
    _status = AuthStatus.unauthenticated;
    _errorMessage = null;
    notifyListeners();
  }

  // Verify email
  Future<bool> verifyEmail(String token) async {
    try {
      final success = await _authService.verifyEmail(token);
      if (success && _user != null) {
        // Update user verification status
        _user = User(
          id: _user!.id,
          email: _user!.email,
          role: _user!.role,
          isVerified: true,
          firstName: _user!.firstName,
          lastName: _user!.lastName,
          phone: _user!.phone,
          createdAt: _user!.createdAt,
        );
        notifyListeners();
      }
      return success;
    } catch (e) {
      print('Email verification error: $e');
      return false;
    }
  }

  // Request password reset
  Future<bool> forgotPassword(String email) async {
    try {
      return await _authService.forgotPassword(email);
    } catch (e) {
      _setError(e.toString());
      return false;
    }
  }

  // Reset password
  Future<bool> resetPassword(String token, String newPassword) async {
    try {
      return await _authService.resetPassword(token, newPassword);
    } catch (e) {
      _setError(e.toString());
      return false;
    }
  }

  // Refresh user data
  Future<void> _refreshUserData() async {
    try {
      final user = await _authService.getCurrentUser();
      if (user != null) {
        _user = user;
        notifyListeners();
      }
    } catch (e) {
      print('Error refreshing user data: $e');
    }
  }

  // Clear error message
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  // Private helper methods
  void _setLoading() {
    _status = AuthStatus.loading;
    _errorMessage = null;
    notifyListeners();
  }

  void _setError(String error) {
    _status = AuthStatus.unauthenticated;
    _errorMessage = error;
    notifyListeners();
  }
}