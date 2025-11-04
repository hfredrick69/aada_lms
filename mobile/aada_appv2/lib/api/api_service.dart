import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = 'https://aada-backend-app12345.azurewebsites.net';

  static Future<Map<String, dynamic>?> login(String email) async {
    final uri = Uri.parse('$baseUrl/auth/login').replace(queryParameters: {'email': email});
    final response = await http.get(uri);

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      print('Login failed: ${response.statusCode} - ${response.body}');
      return null;
    }
  }
}