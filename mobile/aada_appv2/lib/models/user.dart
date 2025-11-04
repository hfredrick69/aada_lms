class User {
  final int id;
  final String email;
  final String role;
  final bool isVerified;
  final String? firstName;
  final String? lastName;
  final String? phone;
  final DateTime? createdAt;

  User({
    required this.id,
    required this.email,
    required this.role,
    required this.isVerified,
    this.firstName,
    this.lastName,
    this.phone,
    this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      email: json['email'],
      role: json['role'],
      isVerified: json['is_verified'] ?? false,
      firstName: json['first_name'],
      lastName: json['last_name'],
      phone: json['phone'],
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'role': role,
      'is_verified': isVerified,
      'first_name': firstName,
      'last_name': lastName,
      'phone': phone,
      'created_at': createdAt?.toIso8601String(),
    };
  }

  String get fullName {
    if (firstName != null && lastName != null) {
      return '$firstName $lastName';
    }
    return email;
  }

  bool get isStudent => role == 'student';
  bool get isInstructor => role == 'instructor';
  bool get isAdmin => role == 'admin';
}

class AuthResponse {
  final String accessToken;
  final String refreshToken;
  final String tokenType;
  final User user;

  AuthResponse({
    required this.accessToken,
    required this.refreshToken,
    required this.tokenType,
    required this.user,
  });

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      accessToken: json['access_token'],
      refreshToken: json['refresh_token'],
      tokenType: json['token_type'] ?? 'bearer',
      user: User.fromJson(json['user']),
    );
  }
}

class RegisterRequest {
  final String email;
  final String password;
  final String firstName;
  final String lastName;
  final String role;

  RegisterRequest({
    required this.email,
    required this.password,
    required this.firstName,
    required this.lastName,
    this.role = 'student',
  });

  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'password': password,
      'first_name': firstName,
      'last_name': lastName,
      'role': role,
    };
  }
}

class LoginRequest {
  final String email;
  final String password;

  LoginRequest({
    required this.email,
    required this.password,
  });

  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'password': password,
    };
  }
}