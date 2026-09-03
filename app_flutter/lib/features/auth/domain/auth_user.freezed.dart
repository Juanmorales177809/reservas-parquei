// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'auth_user.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$LaboratorioResumen {

 int get id; String get nombre; String get ubicacion;
/// Create a copy of LaboratorioResumen
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$LaboratorioResumenCopyWith<LaboratorioResumen> get copyWith => _$LaboratorioResumenCopyWithImpl<LaboratorioResumen>(this as LaboratorioResumen, _$identity);

  /// Serializes this LaboratorioResumen to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is LaboratorioResumen&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.ubicacion, ubicacion) || other.ubicacion == ubicacion));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,ubicacion);

@override
String toString() {
  return 'LaboratorioResumen(id: $id, nombre: $nombre, ubicacion: $ubicacion)';
}


}

/// @nodoc
abstract mixin class $LaboratorioResumenCopyWith<$Res>  {
  factory $LaboratorioResumenCopyWith(LaboratorioResumen value, $Res Function(LaboratorioResumen) _then) = _$LaboratorioResumenCopyWithImpl;
@useResult
$Res call({
 int id, String nombre, String ubicacion
});




}
/// @nodoc
class _$LaboratorioResumenCopyWithImpl<$Res>
    implements $LaboratorioResumenCopyWith<$Res> {
  _$LaboratorioResumenCopyWithImpl(this._self, this._then);

  final LaboratorioResumen _self;
  final $Res Function(LaboratorioResumen) _then;

/// Create a copy of LaboratorioResumen
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? nombre = null,Object? ubicacion = null,}) {
  return _then(LaboratorioResumen(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,ubicacion: null == ubicacion ? _self.ubicacion : ubicacion // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [LaboratorioResumen].
extension LaboratorioResumenPatterns on LaboratorioResumen {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _LaboratorioResumen value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _LaboratorioResumen() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _LaboratorioResumen value)  $default,){
final _that = this;
switch (_that) {
case _LaboratorioResumen():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _LaboratorioResumen value)?  $default,){
final _that = this;
switch (_that) {
case _LaboratorioResumen() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  String nombre,  String ubicacion)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _LaboratorioResumen() when $default != null:
return $default(_that.id,_that.nombre,_that.ubicacion);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  String nombre,  String ubicacion)  $default,) {final _that = this;
switch (_that) {
case _LaboratorioResumen():
return $default(_that.id,_that.nombre,_that.ubicacion);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  String nombre,  String ubicacion)?  $default,) {final _that = this;
switch (_that) {
case _LaboratorioResumen() when $default != null:
return $default(_that.id,_that.nombre,_that.ubicacion);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _LaboratorioResumen implements LaboratorioResumen {
  const _LaboratorioResumen({required this.id, required this.nombre, required this.ubicacion});
  factory _LaboratorioResumen.fromJson(Map<String, dynamic> json) => _$LaboratorioResumenFromJson(json);

@override final  int id;
@override final  String nombre;
@override final  String ubicacion;

/// Create a copy of LaboratorioResumen
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$LaboratorioResumenCopyWith<_LaboratorioResumen> get copyWith => __$LaboratorioResumenCopyWithImpl<_LaboratorioResumen>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$LaboratorioResumenToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _LaboratorioResumen&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.ubicacion, ubicacion) || other.ubicacion == ubicacion));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,ubicacion);

@override
String toString() {
  return 'LaboratorioResumen(id: $id, nombre: $nombre, ubicacion: $ubicacion)';
}


}

/// @nodoc
abstract mixin class _$LaboratorioResumenCopyWith<$Res> implements $LaboratorioResumenCopyWith<$Res> {
  factory _$LaboratorioResumenCopyWith(_LaboratorioResumen value, $Res Function(_LaboratorioResumen) _then) = __$LaboratorioResumenCopyWithImpl;
@override @useResult
$Res call({
 int id, String nombre, String ubicacion
});




}
/// @nodoc
class __$LaboratorioResumenCopyWithImpl<$Res>
    implements _$LaboratorioResumenCopyWith<$Res> {
  __$LaboratorioResumenCopyWithImpl(this._self, this._then);

  final _LaboratorioResumen _self;
  final $Res Function(_LaboratorioResumen) _then;

/// Create a copy of LaboratorioResumen
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? nombre = null,Object? ubicacion = null,}) {
  return _then(_LaboratorioResumen(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,ubicacion: null == ubicacion ? _self.ubicacion : ubicacion // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$AuthUser {

 int get id; String get username; String get email; RolUsuario get rol; LaboratorioResumen? get laboratorio; String? get documentoIdentificacion; String? get telefono; String? get institucion; VinculacionUsuario? get vinculacion; String? get dependencia; bool get recibirCorreos;
/// Create a copy of AuthUser
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AuthUserCopyWith<AuthUser> get copyWith => _$AuthUserCopyWithImpl<AuthUser>(this as AuthUser, _$identity);

  /// Serializes this AuthUser to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AuthUser&&(identical(other.id, id) || other.id == id)&&(identical(other.username, username) || other.username == username)&&(identical(other.email, email) || other.email == email)&&(identical(other.rol, rol) || other.rol == rol)&&(identical(other.laboratorio, laboratorio) || other.laboratorio == laboratorio)&&(identical(other.documentoIdentificacion, documentoIdentificacion) || other.documentoIdentificacion == documentoIdentificacion)&&(identical(other.telefono, telefono) || other.telefono == telefono)&&(identical(other.institucion, institucion) || other.institucion == institucion)&&(identical(other.vinculacion, vinculacion) || other.vinculacion == vinculacion)&&(identical(other.dependencia, dependencia) || other.dependencia == dependencia)&&(identical(other.recibirCorreos, recibirCorreos) || other.recibirCorreos == recibirCorreos));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,username,email,rol,laboratorio,documentoIdentificacion,telefono,institucion,vinculacion,dependencia,recibirCorreos);

@override
String toString() {
  return 'AuthUser(id: $id, username: $username, email: $email, rol: $rol, laboratorio: $laboratorio, documentoIdentificacion: $documentoIdentificacion, telefono: $telefono, institucion: $institucion, vinculacion: $vinculacion, dependencia: $dependencia, recibirCorreos: $recibirCorreos)';
}


}

/// @nodoc
abstract mixin class $AuthUserCopyWith<$Res>  {
  factory $AuthUserCopyWith(AuthUser value, $Res Function(AuthUser) _then) = _$AuthUserCopyWithImpl;
@useResult
$Res call({
 int id, String username, String email, RolUsuario rol, LaboratorioResumen? laboratorio, String? documentoIdentificacion, String? telefono, String? institucion, VinculacionUsuario? vinculacion, String? dependencia, bool recibirCorreos
});


$LaboratorioResumenCopyWith<$Res>? get laboratorio;

}
/// @nodoc
class _$AuthUserCopyWithImpl<$Res>
    implements $AuthUserCopyWith<$Res> {
  _$AuthUserCopyWithImpl(this._self, this._then);

  final AuthUser _self;
  final $Res Function(AuthUser) _then;

/// Create a copy of AuthUser
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? username = null,Object? email = null,Object? rol = null,Object? laboratorio = freezed,Object? documentoIdentificacion = freezed,Object? telefono = freezed,Object? institucion = freezed,Object? vinculacion = freezed,Object? dependencia = freezed,Object? recibirCorreos = null,}) {
  return _then(AuthUser(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,username: null == username ? _self.username : username // ignore: cast_nullable_to_non_nullable
as String,email: null == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String,rol: null == rol ? _self.rol : rol // ignore: cast_nullable_to_non_nullable
as RolUsuario,laboratorio: freezed == laboratorio ? _self.laboratorio : laboratorio // ignore: cast_nullable_to_non_nullable
as LaboratorioResumen?,documentoIdentificacion: freezed == documentoIdentificacion ? _self.documentoIdentificacion : documentoIdentificacion // ignore: cast_nullable_to_non_nullable
as String?,telefono: freezed == telefono ? _self.telefono : telefono // ignore: cast_nullable_to_non_nullable
as String?,institucion: freezed == institucion ? _self.institucion : institucion // ignore: cast_nullable_to_non_nullable
as String?,vinculacion: freezed == vinculacion ? _self.vinculacion : vinculacion // ignore: cast_nullable_to_non_nullable
as VinculacionUsuario?,dependencia: freezed == dependencia ? _self.dependencia : dependencia // ignore: cast_nullable_to_non_nullable
as String?,recibirCorreos: null == recibirCorreos ? _self.recibirCorreos : recibirCorreos // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}
/// Create a copy of AuthUser
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$LaboratorioResumenCopyWith<$Res>? get laboratorio {
    if (_self.laboratorio == null) {
    return null;
  }

  return $LaboratorioResumenCopyWith<$Res>(_self.laboratorio!, (value) {
    return _then(_self.copyWith(laboratorio: value));
  });
}
}


/// Adds pattern-matching-related methods to [AuthUser].
extension AuthUserPatterns on AuthUser {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _AuthUser value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _AuthUser() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _AuthUser value)  $default,){
final _that = this;
switch (_that) {
case _AuthUser():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _AuthUser value)?  $default,){
final _that = this;
switch (_that) {
case _AuthUser() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  String username,  String email,  RolUsuario rol,  LaboratorioResumen? laboratorio,  String? documentoIdentificacion,  String? telefono,  String? institucion,  VinculacionUsuario? vinculacion,  String? dependencia,  bool recibirCorreos)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _AuthUser() when $default != null:
return $default(_that.id,_that.username,_that.email,_that.rol,_that.laboratorio,_that.documentoIdentificacion,_that.telefono,_that.institucion,_that.vinculacion,_that.dependencia,_that.recibirCorreos);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  String username,  String email,  RolUsuario rol,  LaboratorioResumen? laboratorio,  String? documentoIdentificacion,  String? telefono,  String? institucion,  VinculacionUsuario? vinculacion,  String? dependencia,  bool recibirCorreos)  $default,) {final _that = this;
switch (_that) {
case _AuthUser():
return $default(_that.id,_that.username,_that.email,_that.rol,_that.laboratorio,_that.documentoIdentificacion,_that.telefono,_that.institucion,_that.vinculacion,_that.dependencia,_that.recibirCorreos);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  String username,  String email,  RolUsuario rol,  LaboratorioResumen? laboratorio,  String? documentoIdentificacion,  String? telefono,  String? institucion,  VinculacionUsuario? vinculacion,  String? dependencia,  bool recibirCorreos)?  $default,) {final _that = this;
switch (_that) {
case _AuthUser() when $default != null:
return $default(_that.id,_that.username,_that.email,_that.rol,_that.laboratorio,_that.documentoIdentificacion,_that.telefono,_that.institucion,_that.vinculacion,_that.dependencia,_that.recibirCorreos);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _AuthUser extends AuthUser {
  const _AuthUser({required this.id, required this.username, required this.email, required this.rol, this.laboratorio, this.documentoIdentificacion, this.telefono, this.institucion, this.vinculacion, this.dependencia, this.recibirCorreos = true}): super._();
  factory _AuthUser.fromJson(Map<String, dynamic> json) => _$AuthUserFromJson(json);

@override final  int id;
@override final  String username;
@override final  String email;
@override final  RolUsuario rol;
@override final  LaboratorioResumen? laboratorio;
@override final  String? documentoIdentificacion;
@override final  String? telefono;
@override final  String? institucion;
@override final  VinculacionUsuario? vinculacion;
@override final  String? dependencia;
@override@JsonKey() final  bool recibirCorreos;

/// Create a copy of AuthUser
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$AuthUserCopyWith<_AuthUser> get copyWith => __$AuthUserCopyWithImpl<_AuthUser>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$AuthUserToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _AuthUser&&(identical(other.id, id) || other.id == id)&&(identical(other.username, username) || other.username == username)&&(identical(other.email, email) || other.email == email)&&(identical(other.rol, rol) || other.rol == rol)&&(identical(other.laboratorio, laboratorio) || other.laboratorio == laboratorio)&&(identical(other.documentoIdentificacion, documentoIdentificacion) || other.documentoIdentificacion == documentoIdentificacion)&&(identical(other.telefono, telefono) || other.telefono == telefono)&&(identical(other.institucion, institucion) || other.institucion == institucion)&&(identical(other.vinculacion, vinculacion) || other.vinculacion == vinculacion)&&(identical(other.dependencia, dependencia) || other.dependencia == dependencia)&&(identical(other.recibirCorreos, recibirCorreos) || other.recibirCorreos == recibirCorreos));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,username,email,rol,laboratorio,documentoIdentificacion,telefono,institucion,vinculacion,dependencia,recibirCorreos);

@override
String toString() {
  return 'AuthUser(id: $id, username: $username, email: $email, rol: $rol, laboratorio: $laboratorio, documentoIdentificacion: $documentoIdentificacion, telefono: $telefono, institucion: $institucion, vinculacion: $vinculacion, dependencia: $dependencia, recibirCorreos: $recibirCorreos)';
}


}

/// @nodoc
abstract mixin class _$AuthUserCopyWith<$Res> implements $AuthUserCopyWith<$Res> {
  factory _$AuthUserCopyWith(_AuthUser value, $Res Function(_AuthUser) _then) = __$AuthUserCopyWithImpl;
@override @useResult
$Res call({
 int id, String username, String email, RolUsuario rol, LaboratorioResumen? laboratorio, String? documentoIdentificacion, String? telefono, String? institucion, VinculacionUsuario? vinculacion, String? dependencia, bool recibirCorreos
});


@override $LaboratorioResumenCopyWith<$Res>? get laboratorio;

}
/// @nodoc
class __$AuthUserCopyWithImpl<$Res>
    implements _$AuthUserCopyWith<$Res> {
  __$AuthUserCopyWithImpl(this._self, this._then);

  final _AuthUser _self;
  final $Res Function(_AuthUser) _then;

/// Create a copy of AuthUser
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? username = null,Object? email = null,Object? rol = null,Object? laboratorio = freezed,Object? documentoIdentificacion = freezed,Object? telefono = freezed,Object? institucion = freezed,Object? vinculacion = freezed,Object? dependencia = freezed,Object? recibirCorreos = null,}) {
  return _then(_AuthUser(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,username: null == username ? _self.username : username // ignore: cast_nullable_to_non_nullable
as String,email: null == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String,rol: null == rol ? _self.rol : rol // ignore: cast_nullable_to_non_nullable
as RolUsuario,laboratorio: freezed == laboratorio ? _self.laboratorio : laboratorio // ignore: cast_nullable_to_non_nullable
as LaboratorioResumen?,documentoIdentificacion: freezed == documentoIdentificacion ? _self.documentoIdentificacion : documentoIdentificacion // ignore: cast_nullable_to_non_nullable
as String?,telefono: freezed == telefono ? _self.telefono : telefono // ignore: cast_nullable_to_non_nullable
as String?,institucion: freezed == institucion ? _self.institucion : institucion // ignore: cast_nullable_to_non_nullable
as String?,vinculacion: freezed == vinculacion ? _self.vinculacion : vinculacion // ignore: cast_nullable_to_non_nullable
as VinculacionUsuario?,dependencia: freezed == dependencia ? _self.dependencia : dependencia // ignore: cast_nullable_to_non_nullable
as String?,recibirCorreos: null == recibirCorreos ? _self.recibirCorreos : recibirCorreos // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

/// Create a copy of AuthUser
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$LaboratorioResumenCopyWith<$Res>? get laboratorio {
    if (_self.laboratorio == null) {
    return null;
  }

  return $LaboratorioResumenCopyWith<$Res>(_self.laboratorio!, (value) {
    return _then(_self.copyWith(laboratorio: value));
  });
}
}


/// @nodoc
mixin _$LoginResponse {

 AuthUser get user;
/// Create a copy of LoginResponse
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$LoginResponseCopyWith<LoginResponse> get copyWith => _$LoginResponseCopyWithImpl<LoginResponse>(this as LoginResponse, _$identity);

  /// Serializes this LoginResponse to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is LoginResponse&&(identical(other.user, user) || other.user == user));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,user);

@override
String toString() {
  return 'LoginResponse(user: $user)';
}


}

/// @nodoc
abstract mixin class $LoginResponseCopyWith<$Res>  {
  factory $LoginResponseCopyWith(LoginResponse value, $Res Function(LoginResponse) _then) = _$LoginResponseCopyWithImpl;
@useResult
$Res call({
 AuthUser user
});


$AuthUserCopyWith<$Res> get user;

}
/// @nodoc
class _$LoginResponseCopyWithImpl<$Res>
    implements $LoginResponseCopyWith<$Res> {
  _$LoginResponseCopyWithImpl(this._self, this._then);

  final LoginResponse _self;
  final $Res Function(LoginResponse) _then;

/// Create a copy of LoginResponse
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? user = null,}) {
  return _then(LoginResponse(
user: null == user ? _self.user : user // ignore: cast_nullable_to_non_nullable
as AuthUser,
  ));
}
/// Create a copy of LoginResponse
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$AuthUserCopyWith<$Res> get user {
  
  return $AuthUserCopyWith<$Res>(_self.user, (value) {
    return _then(_self.copyWith(user: value));
  });
}
}


/// Adds pattern-matching-related methods to [LoginResponse].
extension LoginResponsePatterns on LoginResponse {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _LoginResponse value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _LoginResponse() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _LoginResponse value)  $default,){
final _that = this;
switch (_that) {
case _LoginResponse():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _LoginResponse value)?  $default,){
final _that = this;
switch (_that) {
case _LoginResponse() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( AuthUser user)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _LoginResponse() when $default != null:
return $default(_that.user);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( AuthUser user)  $default,) {final _that = this;
switch (_that) {
case _LoginResponse():
return $default(_that.user);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( AuthUser user)?  $default,) {final _that = this;
switch (_that) {
case _LoginResponse() when $default != null:
return $default(_that.user);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _LoginResponse implements LoginResponse {
  const _LoginResponse({required this.user});
  factory _LoginResponse.fromJson(Map<String, dynamic> json) => _$LoginResponseFromJson(json);

@override final  AuthUser user;

/// Create a copy of LoginResponse
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$LoginResponseCopyWith<_LoginResponse> get copyWith => __$LoginResponseCopyWithImpl<_LoginResponse>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$LoginResponseToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _LoginResponse&&(identical(other.user, user) || other.user == user));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,user);

@override
String toString() {
  return 'LoginResponse(user: $user)';
}


}

/// @nodoc
abstract mixin class _$LoginResponseCopyWith<$Res> implements $LoginResponseCopyWith<$Res> {
  factory _$LoginResponseCopyWith(_LoginResponse value, $Res Function(_LoginResponse) _then) = __$LoginResponseCopyWithImpl;
@override @useResult
$Res call({
 AuthUser user
});


@override $AuthUserCopyWith<$Res> get user;

}
/// @nodoc
class __$LoginResponseCopyWithImpl<$Res>
    implements _$LoginResponseCopyWith<$Res> {
  __$LoginResponseCopyWithImpl(this._self, this._then);

  final _LoginResponse _self;
  final $Res Function(_LoginResponse) _then;

/// Create a copy of LoginResponse
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? user = null,}) {
  return _then(_LoginResponse(
user: null == user ? _self.user : user // ignore: cast_nullable_to_non_nullable
as AuthUser,
  ));
}

/// Create a copy of LoginResponse
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$AuthUserCopyWith<$Res> get user {
  
  return $AuthUserCopyWith<$Res>(_self.user, (value) {
    return _then(_self.copyWith(user: value));
  });
}
}

// dart format on
