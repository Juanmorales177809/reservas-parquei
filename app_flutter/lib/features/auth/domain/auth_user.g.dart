// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'auth_user.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_EspacioResumen _$EspacioResumenFromJson(Map<String, dynamic> json) =>
    _EspacioResumen(
      id: (json['id'] as num).toInt(),
      nombre: json['nombre'] as String,
      ubicacion: json['ubicacion'] as String,
    );

Map<String, dynamic> _$EspacioResumenToJson(_EspacioResumen instance) =>
    <String, dynamic>{
      'id': instance.id,
      'nombre': instance.nombre,
      'ubicacion': instance.ubicacion,
    };

_AuthUser _$AuthUserFromJson(Map<String, dynamic> json) => _AuthUser(
  id: (json['id'] as num).toInt(),
  username: json['username'] as String,
  email: json['email'] as String,
  rol: $enumDecode(_$RolUsuarioEnumMap, json['rol']),
  espacio: json['espacio'] == null
      ? null
      : EspacioResumen.fromJson(json['espacio'] as Map<String, dynamic>),
  debeCambiarPassword: json['debe_cambiar_password'] as bool? ?? false,
);

Map<String, dynamic> _$AuthUserToJson(_AuthUser instance) => <String, dynamic>{
  'id': instance.id,
  'username': instance.username,
  'email': instance.email,
  'rol': _$RolUsuarioEnumMap[instance.rol]!,
  'espacio': instance.espacio,
  'debe_cambiar_password': instance.debeCambiarPassword,
};

const _$RolUsuarioEnumMap = {
  RolUsuario.usuario: 'usuario',
  RolUsuario.gestor: 'gestor',
  RolUsuario.admin: 'admin',
};

_LoginResponse _$LoginResponseFromJson(Map<String, dynamic> json) =>
    _LoginResponse(
      user: AuthUser.fromJson(json['user'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$LoginResponseToJson(_LoginResponse instance) =>
    <String, dynamic>{'user': instance.user};
