// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'auth_user.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_LaboratorioResumen _$LaboratorioResumenFromJson(Map<String, dynamic> json) =>
    _LaboratorioResumen(
      id: (json['id'] as num).toInt(),
      nombre: json['nombre'] as String,
      ubicacion: json['ubicacion'] as String,
    );

Map<String, dynamic> _$LaboratorioResumenToJson(_LaboratorioResumen instance) =>
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
  laboratorio: json['laboratorio'] == null
      ? null
      : LaboratorioResumen.fromJson(
          json['laboratorio'] as Map<String, dynamic>,
        ),
  documentoIdentificacion: json['documento_identificacion'] as String?,
  telefono: json['telefono'] as String?,
  institucion: json['institucion'] as String?,
  vinculacion: $enumDecodeNullable(
    _$VinculacionUsuarioEnumMap,
    json['vinculacion'],
  ),
  dependencia: json['dependencia'] as String?,
);

Map<String, dynamic> _$AuthUserToJson(_AuthUser instance) => <String, dynamic>{
  'id': instance.id,
  'username': instance.username,
  'email': instance.email,
  'rol': _$RolUsuarioEnumMap[instance.rol]!,
  'laboratorio': instance.laboratorio,
  'documento_identificacion': instance.documentoIdentificacion,
  'telefono': instance.telefono,
  'institucion': instance.institucion,
  'vinculacion': _$VinculacionUsuarioEnumMap[instance.vinculacion],
  'dependencia': instance.dependencia,
};

const _$RolUsuarioEnumMap = {
  RolUsuario.usuario: 'usuario',
  RolUsuario.gestor: 'gestor',
  RolUsuario.admin: 'admin',
};

const _$VinculacionUsuarioEnumMap = {
  VinculacionUsuario.docente: 'docente',
  VinculacionUsuario.estudiante: 'estudiante',
  VinculacionUsuario.contratistaEmpleado: 'contratista_empleado',
  VinculacionUsuario.extension: 'extension',
  VinculacionUsuario.otra: 'otra',
};

_LoginResponse _$LoginResponseFromJson(Map<String, dynamic> json) =>
    _LoginResponse(
      user: AuthUser.fromJson(json['user'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$LoginResponseToJson(_LoginResponse instance) =>
    <String, dynamic>{'user': instance.user};
