// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'reserva.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$UsuarioReserva {

 int get id; String get username; String get email; RolUsuario get rol;
/// Create a copy of UsuarioReserva
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UsuarioReservaCopyWith<UsuarioReserva> get copyWith => _$UsuarioReservaCopyWithImpl<UsuarioReserva>(this as UsuarioReserva, _$identity);

  /// Serializes this UsuarioReserva to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is UsuarioReserva&&(identical(other.id, id) || other.id == id)&&(identical(other.username, username) || other.username == username)&&(identical(other.email, email) || other.email == email)&&(identical(other.rol, rol) || other.rol == rol));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,username,email,rol);

@override
String toString() {
  return 'UsuarioReserva(id: $id, username: $username, email: $email, rol: $rol)';
}


}

/// @nodoc
abstract mixin class $UsuarioReservaCopyWith<$Res>  {
  factory $UsuarioReservaCopyWith(UsuarioReserva value, $Res Function(UsuarioReserva) _then) = _$UsuarioReservaCopyWithImpl;
@useResult
$Res call({
 int id, String username, String email, RolUsuario rol
});




}
/// @nodoc
class _$UsuarioReservaCopyWithImpl<$Res>
    implements $UsuarioReservaCopyWith<$Res> {
  _$UsuarioReservaCopyWithImpl(this._self, this._then);

  final UsuarioReserva _self;
  final $Res Function(UsuarioReserva) _then;

/// Create a copy of UsuarioReserva
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? username = null,Object? email = null,Object? rol = null,}) {
  return _then(UsuarioReserva(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,username: null == username ? _self.username : username // ignore: cast_nullable_to_non_nullable
as String,email: null == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String,rol: null == rol ? _self.rol : rol // ignore: cast_nullable_to_non_nullable
as RolUsuario,
  ));
}

}


/// Adds pattern-matching-related methods to [UsuarioReserva].
extension UsuarioReservaPatterns on UsuarioReserva {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _UsuarioReserva value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _UsuarioReserva() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _UsuarioReserva value)  $default,){
final _that = this;
switch (_that) {
case _UsuarioReserva():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _UsuarioReserva value)?  $default,){
final _that = this;
switch (_that) {
case _UsuarioReserva() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  String username,  String email,  RolUsuario rol)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _UsuarioReserva() when $default != null:
return $default(_that.id,_that.username,_that.email,_that.rol);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  String username,  String email,  RolUsuario rol)  $default,) {final _that = this;
switch (_that) {
case _UsuarioReserva():
return $default(_that.id,_that.username,_that.email,_that.rol);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  String username,  String email,  RolUsuario rol)?  $default,) {final _that = this;
switch (_that) {
case _UsuarioReserva() when $default != null:
return $default(_that.id,_that.username,_that.email,_that.rol);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _UsuarioReserva implements UsuarioReserva {
  const _UsuarioReserva({required this.id, required this.username, required this.email, required this.rol});
  factory _UsuarioReserva.fromJson(Map<String, dynamic> json) => _$UsuarioReservaFromJson(json);

@override final  int id;
@override final  String username;
@override final  String email;
@override final  RolUsuario rol;

/// Create a copy of UsuarioReserva
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$UsuarioReservaCopyWith<_UsuarioReserva> get copyWith => __$UsuarioReservaCopyWithImpl<_UsuarioReserva>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$UsuarioReservaToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _UsuarioReserva&&(identical(other.id, id) || other.id == id)&&(identical(other.username, username) || other.username == username)&&(identical(other.email, email) || other.email == email)&&(identical(other.rol, rol) || other.rol == rol));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,username,email,rol);

@override
String toString() {
  return 'UsuarioReserva(id: $id, username: $username, email: $email, rol: $rol)';
}


}

/// @nodoc
abstract mixin class _$UsuarioReservaCopyWith<$Res> implements $UsuarioReservaCopyWith<$Res> {
  factory _$UsuarioReservaCopyWith(_UsuarioReserva value, $Res Function(_UsuarioReserva) _then) = __$UsuarioReservaCopyWithImpl;
@override @useResult
$Res call({
 int id, String username, String email, RolUsuario rol
});




}
/// @nodoc
class __$UsuarioReservaCopyWithImpl<$Res>
    implements _$UsuarioReservaCopyWith<$Res> {
  __$UsuarioReservaCopyWithImpl(this._self, this._then);

  final _UsuarioReserva _self;
  final $Res Function(_UsuarioReserva) _then;

/// Create a copy of UsuarioReserva
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? username = null,Object? email = null,Object? rol = null,}) {
  return _then(_UsuarioReserva(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,username: null == username ? _self.username : username // ignore: cast_nullable_to_non_nullable
as String,email: null == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String,rol: null == rol ? _self.rol : rol // ignore: cast_nullable_to_non_nullable
as RolUsuario,
  ));
}


}


/// @nodoc
mixin _$LaboratorioReserva {

 int get id; String get nombre; int? get capacidad; EstadoEntidad get estado;
/// Create a copy of LaboratorioReserva
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$LaboratorioReservaCopyWith<LaboratorioReserva> get copyWith => _$LaboratorioReservaCopyWithImpl<LaboratorioReserva>(this as LaboratorioReserva, _$identity);

  /// Serializes this LaboratorioReserva to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is LaboratorioReserva&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.capacidad, capacidad) || other.capacidad == capacidad)&&(identical(other.estado, estado) || other.estado == estado));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,capacidad,estado);

@override
String toString() {
  return 'LaboratorioReserva(id: $id, nombre: $nombre, capacidad: $capacidad, estado: $estado)';
}


}

/// @nodoc
abstract mixin class $LaboratorioReservaCopyWith<$Res>  {
  factory $LaboratorioReservaCopyWith(LaboratorioReserva value, $Res Function(LaboratorioReserva) _then) = _$LaboratorioReservaCopyWithImpl;
@useResult
$Res call({
 int id, String nombre, int? capacidad, EstadoEntidad estado
});




}
/// @nodoc
class _$LaboratorioReservaCopyWithImpl<$Res>
    implements $LaboratorioReservaCopyWith<$Res> {
  _$LaboratorioReservaCopyWithImpl(this._self, this._then);

  final LaboratorioReserva _self;
  final $Res Function(LaboratorioReserva) _then;

/// Create a copy of LaboratorioReserva
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? nombre = null,Object? capacidad = freezed,Object? estado = null,}) {
  return _then(LaboratorioReserva(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,capacidad: freezed == capacidad ? _self.capacidad : capacidad // ignore: cast_nullable_to_non_nullable
as int?,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as EstadoEntidad,
  ));
}

}


/// Adds pattern-matching-related methods to [LaboratorioReserva].
extension LaboratorioReservaPatterns on LaboratorioReserva {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _LaboratorioReserva value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _LaboratorioReserva() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _LaboratorioReserva value)  $default,){
final _that = this;
switch (_that) {
case _LaboratorioReserva():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _LaboratorioReserva value)?  $default,){
final _that = this;
switch (_that) {
case _LaboratorioReserva() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  String nombre,  int? capacidad,  EstadoEntidad estado)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _LaboratorioReserva() when $default != null:
return $default(_that.id,_that.nombre,_that.capacidad,_that.estado);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  String nombre,  int? capacidad,  EstadoEntidad estado)  $default,) {final _that = this;
switch (_that) {
case _LaboratorioReserva():
return $default(_that.id,_that.nombre,_that.capacidad,_that.estado);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  String nombre,  int? capacidad,  EstadoEntidad estado)?  $default,) {final _that = this;
switch (_that) {
case _LaboratorioReserva() when $default != null:
return $default(_that.id,_that.nombre,_that.capacidad,_that.estado);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _LaboratorioReserva implements LaboratorioReserva {
  const _LaboratorioReserva({required this.id, required this.nombre, this.capacidad, required this.estado});
  factory _LaboratorioReserva.fromJson(Map<String, dynamic> json) => _$LaboratorioReservaFromJson(json);

@override final  int id;
@override final  String nombre;
@override final  int? capacidad;
@override final  EstadoEntidad estado;

/// Create a copy of LaboratorioReserva
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$LaboratorioReservaCopyWith<_LaboratorioReserva> get copyWith => __$LaboratorioReservaCopyWithImpl<_LaboratorioReserva>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$LaboratorioReservaToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _LaboratorioReserva&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.capacidad, capacidad) || other.capacidad == capacidad)&&(identical(other.estado, estado) || other.estado == estado));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,capacidad,estado);

@override
String toString() {
  return 'LaboratorioReserva(id: $id, nombre: $nombre, capacidad: $capacidad, estado: $estado)';
}


}

/// @nodoc
abstract mixin class _$LaboratorioReservaCopyWith<$Res> implements $LaboratorioReservaCopyWith<$Res> {
  factory _$LaboratorioReservaCopyWith(_LaboratorioReserva value, $Res Function(_LaboratorioReserva) _then) = __$LaboratorioReservaCopyWithImpl;
@override @useResult
$Res call({
 int id, String nombre, int? capacidad, EstadoEntidad estado
});




}
/// @nodoc
class __$LaboratorioReservaCopyWithImpl<$Res>
    implements _$LaboratorioReservaCopyWith<$Res> {
  __$LaboratorioReservaCopyWithImpl(this._self, this._then);

  final _LaboratorioReserva _self;
  final $Res Function(_LaboratorioReserva) _then;

/// Create a copy of LaboratorioReserva
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? nombre = null,Object? capacidad = freezed,Object? estado = null,}) {
  return _then(_LaboratorioReserva(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,capacidad: freezed == capacidad ? _self.capacidad : capacidad // ignore: cast_nullable_to_non_nullable
as int?,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as EstadoEntidad,
  ));
}


}


/// @nodoc
mixin _$RecursoReserva {

 int get id; String get nombre; int? get capacidad; EstadoEntidad get estado; LaboratorioReserva get laboratorio;
/// Create a copy of RecursoReserva
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RecursoReservaCopyWith<RecursoReserva> get copyWith => _$RecursoReservaCopyWithImpl<RecursoReserva>(this as RecursoReserva, _$identity);

  /// Serializes this RecursoReserva to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is RecursoReserva&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.capacidad, capacidad) || other.capacidad == capacidad)&&(identical(other.estado, estado) || other.estado == estado)&&(identical(other.laboratorio, laboratorio) || other.laboratorio == laboratorio));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,capacidad,estado,laboratorio);

@override
String toString() {
  return 'RecursoReserva(id: $id, nombre: $nombre, capacidad: $capacidad, estado: $estado, laboratorio: $laboratorio)';
}


}

/// @nodoc
abstract mixin class $RecursoReservaCopyWith<$Res>  {
  factory $RecursoReservaCopyWith(RecursoReserva value, $Res Function(RecursoReserva) _then) = _$RecursoReservaCopyWithImpl;
@useResult
$Res call({
 int id, String nombre, int? capacidad, EstadoEntidad estado, LaboratorioReserva laboratorio
});


$LaboratorioReservaCopyWith<$Res> get laboratorio;

}
/// @nodoc
class _$RecursoReservaCopyWithImpl<$Res>
    implements $RecursoReservaCopyWith<$Res> {
  _$RecursoReservaCopyWithImpl(this._self, this._then);

  final RecursoReserva _self;
  final $Res Function(RecursoReserva) _then;

/// Create a copy of RecursoReserva
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? nombre = null,Object? capacidad = freezed,Object? estado = null,Object? laboratorio = null,}) {
  return _then(RecursoReserva(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,capacidad: freezed == capacidad ? _self.capacidad : capacidad // ignore: cast_nullable_to_non_nullable
as int?,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as EstadoEntidad,laboratorio: null == laboratorio ? _self.laboratorio : laboratorio // ignore: cast_nullable_to_non_nullable
as LaboratorioReserva,
  ));
}
/// Create a copy of RecursoReserva
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$LaboratorioReservaCopyWith<$Res> get laboratorio {
  
  return $LaboratorioReservaCopyWith<$Res>(_self.laboratorio, (value) {
    return _then(_self.copyWith(laboratorio: value));
  });
}
}


/// Adds pattern-matching-related methods to [RecursoReserva].
extension RecursoReservaPatterns on RecursoReserva {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _RecursoReserva value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _RecursoReserva() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _RecursoReserva value)  $default,){
final _that = this;
switch (_that) {
case _RecursoReserva():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _RecursoReserva value)?  $default,){
final _that = this;
switch (_that) {
case _RecursoReserva() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  String nombre,  int? capacidad,  EstadoEntidad estado,  LaboratorioReserva laboratorio)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _RecursoReserva() when $default != null:
return $default(_that.id,_that.nombre,_that.capacidad,_that.estado,_that.laboratorio);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  String nombre,  int? capacidad,  EstadoEntidad estado,  LaboratorioReserva laboratorio)  $default,) {final _that = this;
switch (_that) {
case _RecursoReserva():
return $default(_that.id,_that.nombre,_that.capacidad,_that.estado,_that.laboratorio);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  String nombre,  int? capacidad,  EstadoEntidad estado,  LaboratorioReserva laboratorio)?  $default,) {final _that = this;
switch (_that) {
case _RecursoReserva() when $default != null:
return $default(_that.id,_that.nombre,_that.capacidad,_that.estado,_that.laboratorio);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _RecursoReserva implements RecursoReserva {
  const _RecursoReserva({required this.id, required this.nombre, this.capacidad, required this.estado, required this.laboratorio});
  factory _RecursoReserva.fromJson(Map<String, dynamic> json) => _$RecursoReservaFromJson(json);

@override final  int id;
@override final  String nombre;
@override final  int? capacidad;
@override final  EstadoEntidad estado;
@override final  LaboratorioReserva laboratorio;

/// Create a copy of RecursoReserva
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$RecursoReservaCopyWith<_RecursoReserva> get copyWith => __$RecursoReservaCopyWithImpl<_RecursoReserva>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$RecursoReservaToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _RecursoReserva&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.capacidad, capacidad) || other.capacidad == capacidad)&&(identical(other.estado, estado) || other.estado == estado)&&(identical(other.laboratorio, laboratorio) || other.laboratorio == laboratorio));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,capacidad,estado,laboratorio);

@override
String toString() {
  return 'RecursoReserva(id: $id, nombre: $nombre, capacidad: $capacidad, estado: $estado, laboratorio: $laboratorio)';
}


}

/// @nodoc
abstract mixin class _$RecursoReservaCopyWith<$Res> implements $RecursoReservaCopyWith<$Res> {
  factory _$RecursoReservaCopyWith(_RecursoReserva value, $Res Function(_RecursoReserva) _then) = __$RecursoReservaCopyWithImpl;
@override @useResult
$Res call({
 int id, String nombre, int? capacidad, EstadoEntidad estado, LaboratorioReserva laboratorio
});


@override $LaboratorioReservaCopyWith<$Res> get laboratorio;

}
/// @nodoc
class __$RecursoReservaCopyWithImpl<$Res>
    implements _$RecursoReservaCopyWith<$Res> {
  __$RecursoReservaCopyWithImpl(this._self, this._then);

  final _RecursoReserva _self;
  final $Res Function(_RecursoReserva) _then;

/// Create a copy of RecursoReserva
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? nombre = null,Object? capacidad = freezed,Object? estado = null,Object? laboratorio = null,}) {
  return _then(_RecursoReserva(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,capacidad: freezed == capacidad ? _self.capacidad : capacidad // ignore: cast_nullable_to_non_nullable
as int?,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as EstadoEntidad,laboratorio: null == laboratorio ? _self.laboratorio : laboratorio // ignore: cast_nullable_to_non_nullable
as LaboratorioReserva,
  ));
}

/// Create a copy of RecursoReserva
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$LaboratorioReservaCopyWith<$Res> get laboratorio {
  
  return $LaboratorioReservaCopyWith<$Res>(_self.laboratorio, (value) {
    return _then(_self.copyWith(laboratorio: value));
  });
}
}


/// @nodoc
mixin _$EspacioReserva {

 int get id; String get nombre; int get laboratorioId; String? get descripcion; int? get capacidad; EstadoEntidad get estado;
/// Create a copy of EspacioReserva
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$EspacioReservaCopyWith<EspacioReserva> get copyWith => _$EspacioReservaCopyWithImpl<EspacioReserva>(this as EspacioReserva, _$identity);

  /// Serializes this EspacioReserva to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is EspacioReserva&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.laboratorioId, laboratorioId) || other.laboratorioId == laboratorioId)&&(identical(other.descripcion, descripcion) || other.descripcion == descripcion)&&(identical(other.capacidad, capacidad) || other.capacidad == capacidad)&&(identical(other.estado, estado) || other.estado == estado));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,laboratorioId,descripcion,capacidad,estado);

@override
String toString() {
  return 'EspacioReserva(id: $id, nombre: $nombre, laboratorioId: $laboratorioId, descripcion: $descripcion, capacidad: $capacidad, estado: $estado)';
}


}

/// @nodoc
abstract mixin class $EspacioReservaCopyWith<$Res>  {
  factory $EspacioReservaCopyWith(EspacioReserva value, $Res Function(EspacioReserva) _then) = _$EspacioReservaCopyWithImpl;
@useResult
$Res call({
 int id, String nombre, int laboratorioId, String? descripcion, int? capacidad, EstadoEntidad estado
});




}
/// @nodoc
class _$EspacioReservaCopyWithImpl<$Res>
    implements $EspacioReservaCopyWith<$Res> {
  _$EspacioReservaCopyWithImpl(this._self, this._then);

  final EspacioReserva _self;
  final $Res Function(EspacioReserva) _then;

/// Create a copy of EspacioReserva
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? nombre = null,Object? laboratorioId = null,Object? descripcion = freezed,Object? capacidad = freezed,Object? estado = null,}) {
  return _then(EspacioReserva(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,laboratorioId: null == laboratorioId ? _self.laboratorioId : laboratorioId // ignore: cast_nullable_to_non_nullable
as int,descripcion: freezed == descripcion ? _self.descripcion : descripcion // ignore: cast_nullable_to_non_nullable
as String?,capacidad: freezed == capacidad ? _self.capacidad : capacidad // ignore: cast_nullable_to_non_nullable
as int?,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as EstadoEntidad,
  ));
}

}


/// Adds pattern-matching-related methods to [EspacioReserva].
extension EspacioReservaPatterns on EspacioReserva {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _EspacioReserva value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _EspacioReserva() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _EspacioReserva value)  $default,){
final _that = this;
switch (_that) {
case _EspacioReserva():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _EspacioReserva value)?  $default,){
final _that = this;
switch (_that) {
case _EspacioReserva() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  String nombre,  int laboratorioId,  String? descripcion,  int? capacidad,  EstadoEntidad estado)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _EspacioReserva() when $default != null:
return $default(_that.id,_that.nombre,_that.laboratorioId,_that.descripcion,_that.capacidad,_that.estado);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  String nombre,  int laboratorioId,  String? descripcion,  int? capacidad,  EstadoEntidad estado)  $default,) {final _that = this;
switch (_that) {
case _EspacioReserva():
return $default(_that.id,_that.nombre,_that.laboratorioId,_that.descripcion,_that.capacidad,_that.estado);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  String nombre,  int laboratorioId,  String? descripcion,  int? capacidad,  EstadoEntidad estado)?  $default,) {final _that = this;
switch (_that) {
case _EspacioReserva() when $default != null:
return $default(_that.id,_that.nombre,_that.laboratorioId,_that.descripcion,_that.capacidad,_that.estado);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _EspacioReserva implements EspacioReserva {
  const _EspacioReserva({required this.id, required this.nombre, required this.laboratorioId, this.descripcion, this.capacidad, required this.estado});
  factory _EspacioReserva.fromJson(Map<String, dynamic> json) => _$EspacioReservaFromJson(json);

@override final  int id;
@override final  String nombre;
@override final  int laboratorioId;
@override final  String? descripcion;
@override final  int? capacidad;
@override final  EstadoEntidad estado;

/// Create a copy of EspacioReserva
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$EspacioReservaCopyWith<_EspacioReserva> get copyWith => __$EspacioReservaCopyWithImpl<_EspacioReserva>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$EspacioReservaToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _EspacioReserva&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.laboratorioId, laboratorioId) || other.laboratorioId == laboratorioId)&&(identical(other.descripcion, descripcion) || other.descripcion == descripcion)&&(identical(other.capacidad, capacidad) || other.capacidad == capacidad)&&(identical(other.estado, estado) || other.estado == estado));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,laboratorioId,descripcion,capacidad,estado);

@override
String toString() {
  return 'EspacioReserva(id: $id, nombre: $nombre, laboratorioId: $laboratorioId, descripcion: $descripcion, capacidad: $capacidad, estado: $estado)';
}


}

/// @nodoc
abstract mixin class _$EspacioReservaCopyWith<$Res> implements $EspacioReservaCopyWith<$Res> {
  factory _$EspacioReservaCopyWith(_EspacioReserva value, $Res Function(_EspacioReserva) _then) = __$EspacioReservaCopyWithImpl;
@override @useResult
$Res call({
 int id, String nombre, int laboratorioId, String? descripcion, int? capacidad, EstadoEntidad estado
});




}
/// @nodoc
class __$EspacioReservaCopyWithImpl<$Res>
    implements _$EspacioReservaCopyWith<$Res> {
  __$EspacioReservaCopyWithImpl(this._self, this._then);

  final _EspacioReserva _self;
  final $Res Function(_EspacioReserva) _then;

/// Create a copy of EspacioReserva
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? nombre = null,Object? laboratorioId = null,Object? descripcion = freezed,Object? capacidad = freezed,Object? estado = null,}) {
  return _then(_EspacioReserva(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,laboratorioId: null == laboratorioId ? _self.laboratorioId : laboratorioId // ignore: cast_nullable_to_non_nullable
as int,descripcion: freezed == descripcion ? _self.descripcion : descripcion // ignore: cast_nullable_to_non_nullable
as String?,capacidad: freezed == capacidad ? _self.capacidad : capacidad // ignore: cast_nullable_to_non_nullable
as int?,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as EstadoEntidad,
  ));
}


}


/// @nodoc
mixin _$TipoReservaReserva {

 int get id; int get laboratorioId; String get nombre; String get estado;
/// Create a copy of TipoReservaReserva
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$TipoReservaReservaCopyWith<TipoReservaReserva> get copyWith => _$TipoReservaReservaCopyWithImpl<TipoReservaReserva>(this as TipoReservaReserva, _$identity);

  /// Serializes this TipoReservaReserva to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is TipoReservaReserva&&(identical(other.id, id) || other.id == id)&&(identical(other.laboratorioId, laboratorioId) || other.laboratorioId == laboratorioId)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.estado, estado) || other.estado == estado));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,laboratorioId,nombre,estado);

@override
String toString() {
  return 'TipoReservaReserva(id: $id, laboratorioId: $laboratorioId, nombre: $nombre, estado: $estado)';
}


}

/// @nodoc
abstract mixin class $TipoReservaReservaCopyWith<$Res>  {
  factory $TipoReservaReservaCopyWith(TipoReservaReserva value, $Res Function(TipoReservaReserva) _then) = _$TipoReservaReservaCopyWithImpl;
@useResult
$Res call({
 int id, int laboratorioId, String nombre, String estado
});




}
/// @nodoc
class _$TipoReservaReservaCopyWithImpl<$Res>
    implements $TipoReservaReservaCopyWith<$Res> {
  _$TipoReservaReservaCopyWithImpl(this._self, this._then);

  final TipoReservaReserva _self;
  final $Res Function(TipoReservaReserva) _then;

/// Create a copy of TipoReservaReserva
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? laboratorioId = null,Object? nombre = null,Object? estado = null,}) {
  return _then(TipoReservaReserva(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,laboratorioId: null == laboratorioId ? _self.laboratorioId : laboratorioId // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [TipoReservaReserva].
extension TipoReservaReservaPatterns on TipoReservaReserva {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _TipoReservaReserva value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _TipoReservaReserva() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _TipoReservaReserva value)  $default,){
final _that = this;
switch (_that) {
case _TipoReservaReserva():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _TipoReservaReserva value)?  $default,){
final _that = this;
switch (_that) {
case _TipoReservaReserva() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  int laboratorioId,  String nombre,  String estado)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _TipoReservaReserva() when $default != null:
return $default(_that.id,_that.laboratorioId,_that.nombre,_that.estado);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  int laboratorioId,  String nombre,  String estado)  $default,) {final _that = this;
switch (_that) {
case _TipoReservaReserva():
return $default(_that.id,_that.laboratorioId,_that.nombre,_that.estado);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  int laboratorioId,  String nombre,  String estado)?  $default,) {final _that = this;
switch (_that) {
case _TipoReservaReserva() when $default != null:
return $default(_that.id,_that.laboratorioId,_that.nombre,_that.estado);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _TipoReservaReserva implements TipoReservaReserva {
  const _TipoReservaReserva({required this.id, required this.laboratorioId, required this.nombre, required this.estado});
  factory _TipoReservaReserva.fromJson(Map<String, dynamic> json) => _$TipoReservaReservaFromJson(json);

@override final  int id;
@override final  int laboratorioId;
@override final  String nombre;
@override final  String estado;

/// Create a copy of TipoReservaReserva
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$TipoReservaReservaCopyWith<_TipoReservaReserva> get copyWith => __$TipoReservaReservaCopyWithImpl<_TipoReservaReserva>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$TipoReservaReservaToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _TipoReservaReserva&&(identical(other.id, id) || other.id == id)&&(identical(other.laboratorioId, laboratorioId) || other.laboratorioId == laboratorioId)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.estado, estado) || other.estado == estado));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,laboratorioId,nombre,estado);

@override
String toString() {
  return 'TipoReservaReserva(id: $id, laboratorioId: $laboratorioId, nombre: $nombre, estado: $estado)';
}


}

/// @nodoc
abstract mixin class _$TipoReservaReservaCopyWith<$Res> implements $TipoReservaReservaCopyWith<$Res> {
  factory _$TipoReservaReservaCopyWith(_TipoReservaReserva value, $Res Function(_TipoReservaReserva) _then) = __$TipoReservaReservaCopyWithImpl;
@override @useResult
$Res call({
 int id, int laboratorioId, String nombre, String estado
});




}
/// @nodoc
class __$TipoReservaReservaCopyWithImpl<$Res>
    implements _$TipoReservaReservaCopyWith<$Res> {
  __$TipoReservaReservaCopyWithImpl(this._self, this._then);

  final _TipoReservaReserva _self;
  final $Res Function(_TipoReservaReserva) _then;

/// Create a copy of TipoReservaReserva
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? laboratorioId = null,Object? nombre = null,Object? estado = null,}) {
  return _then(_TipoReservaReserva(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,laboratorioId: null == laboratorioId ? _self.laboratorioId : laboratorioId // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$ReservaAcompanante {

 int get id; String get nombre; String get correo;
/// Create a copy of ReservaAcompanante
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ReservaAcompananteCopyWith<ReservaAcompanante> get copyWith => _$ReservaAcompananteCopyWithImpl<ReservaAcompanante>(this as ReservaAcompanante, _$identity);

  /// Serializes this ReservaAcompanante to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ReservaAcompanante&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.correo, correo) || other.correo == correo));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,correo);

@override
String toString() {
  return 'ReservaAcompanante(id: $id, nombre: $nombre, correo: $correo)';
}


}

/// @nodoc
abstract mixin class $ReservaAcompananteCopyWith<$Res>  {
  factory $ReservaAcompananteCopyWith(ReservaAcompanante value, $Res Function(ReservaAcompanante) _then) = _$ReservaAcompananteCopyWithImpl;
@useResult
$Res call({
 int id, String nombre, String correo
});




}
/// @nodoc
class _$ReservaAcompananteCopyWithImpl<$Res>
    implements $ReservaAcompananteCopyWith<$Res> {
  _$ReservaAcompananteCopyWithImpl(this._self, this._then);

  final ReservaAcompanante _self;
  final $Res Function(ReservaAcompanante) _then;

/// Create a copy of ReservaAcompanante
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? nombre = null,Object? correo = null,}) {
  return _then(ReservaAcompanante(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,correo: null == correo ? _self.correo : correo // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [ReservaAcompanante].
extension ReservaAcompanantePatterns on ReservaAcompanante {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ReservaAcompanante value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ReservaAcompanante() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ReservaAcompanante value)  $default,){
final _that = this;
switch (_that) {
case _ReservaAcompanante():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ReservaAcompanante value)?  $default,){
final _that = this;
switch (_that) {
case _ReservaAcompanante() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  String nombre,  String correo)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ReservaAcompanante() when $default != null:
return $default(_that.id,_that.nombre,_that.correo);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  String nombre,  String correo)  $default,) {final _that = this;
switch (_that) {
case _ReservaAcompanante():
return $default(_that.id,_that.nombre,_that.correo);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  String nombre,  String correo)?  $default,) {final _that = this;
switch (_that) {
case _ReservaAcompanante() when $default != null:
return $default(_that.id,_that.nombre,_that.correo);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ReservaAcompanante implements ReservaAcompanante {
  const _ReservaAcompanante({required this.id, required this.nombre, required this.correo});
  factory _ReservaAcompanante.fromJson(Map<String, dynamic> json) => _$ReservaAcompananteFromJson(json);

@override final  int id;
@override final  String nombre;
@override final  String correo;

/// Create a copy of ReservaAcompanante
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ReservaAcompananteCopyWith<_ReservaAcompanante> get copyWith => __$ReservaAcompananteCopyWithImpl<_ReservaAcompanante>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ReservaAcompananteToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ReservaAcompanante&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.correo, correo) || other.correo == correo));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,correo);

@override
String toString() {
  return 'ReservaAcompanante(id: $id, nombre: $nombre, correo: $correo)';
}


}

/// @nodoc
abstract mixin class _$ReservaAcompananteCopyWith<$Res> implements $ReservaAcompananteCopyWith<$Res> {
  factory _$ReservaAcompananteCopyWith(_ReservaAcompanante value, $Res Function(_ReservaAcompanante) _then) = __$ReservaAcompananteCopyWithImpl;
@override @useResult
$Res call({
 int id, String nombre, String correo
});




}
/// @nodoc
class __$ReservaAcompananteCopyWithImpl<$Res>
    implements _$ReservaAcompananteCopyWith<$Res> {
  __$ReservaAcompananteCopyWithImpl(this._self, this._then);

  final _ReservaAcompanante _self;
  final $Res Function(_ReservaAcompanante) _then;

/// Create a copy of ReservaAcompanante
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? nombre = null,Object? correo = null,}) {
  return _then(_ReservaAcompanante(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,correo: null == correo ? _self.correo : correo // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$Reserva {

 int get id; int get usuarioId; int get laboratorioId; String get fecha; String get horaInicio; String get horaFin; EstadoReserva get estado; int get asistentes; TipoReserva? get tipo; int? get tipoReservaId; TipoReservaReserva? get tipoReserva; int? get motivoSolicitudId; String? get motivoSolicitudCodigo; String? get motivoSolicitudNombre; bool? get asistio; String? get motivoRechazo; String? get propuestaMotivo; String? get propuestaHorarios; String? get propuestaPor; String? get propuestaEn; String? get descripcion; TipoSolicitud get tipoSolicitud; String? get ubicacionUso; bool get requiereApoyoAuxiliar; String get createdAt; String get updatedAt; UsuarioReserva get usuario; LaboratorioReserva get laboratorio; List<int> get recursoIds; List<RecursoReserva> get recursos; List<int> get espacioIds; List<EspacioReserva> get espacios; List<ReservaAcompanante> get acompanantes;
/// Create a copy of Reserva
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ReservaCopyWith<Reserva> get copyWith => _$ReservaCopyWithImpl<Reserva>(this as Reserva, _$identity);

  /// Serializes this Reserva to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Reserva&&(identical(other.id, id) || other.id == id)&&(identical(other.usuarioId, usuarioId) || other.usuarioId == usuarioId)&&(identical(other.laboratorioId, laboratorioId) || other.laboratorioId == laboratorioId)&&(identical(other.fecha, fecha) || other.fecha == fecha)&&(identical(other.horaInicio, horaInicio) || other.horaInicio == horaInicio)&&(identical(other.horaFin, horaFin) || other.horaFin == horaFin)&&(identical(other.estado, estado) || other.estado == estado)&&(identical(other.asistentes, asistentes) || other.asistentes == asistentes)&&(identical(other.tipo, tipo) || other.tipo == tipo)&&(identical(other.tipoReservaId, tipoReservaId) || other.tipoReservaId == tipoReservaId)&&(identical(other.tipoReserva, tipoReserva) || other.tipoReserva == tipoReserva)&&(identical(other.motivoSolicitudId, motivoSolicitudId) || other.motivoSolicitudId == motivoSolicitudId)&&(identical(other.motivoSolicitudCodigo, motivoSolicitudCodigo) || other.motivoSolicitudCodigo == motivoSolicitudCodigo)&&(identical(other.motivoSolicitudNombre, motivoSolicitudNombre) || other.motivoSolicitudNombre == motivoSolicitudNombre)&&(identical(other.asistio, asistio) || other.asistio == asistio)&&(identical(other.motivoRechazo, motivoRechazo) || other.motivoRechazo == motivoRechazo)&&(identical(other.propuestaMotivo, propuestaMotivo) || other.propuestaMotivo == propuestaMotivo)&&(identical(other.propuestaHorarios, propuestaHorarios) || other.propuestaHorarios == propuestaHorarios)&&(identical(other.propuestaPor, propuestaPor) || other.propuestaPor == propuestaPor)&&(identical(other.propuestaEn, propuestaEn) || other.propuestaEn == propuestaEn)&&(identical(other.descripcion, descripcion) || other.descripcion == descripcion)&&(identical(other.tipoSolicitud, tipoSolicitud) || other.tipoSolicitud == tipoSolicitud)&&(identical(other.ubicacionUso, ubicacionUso) || other.ubicacionUso == ubicacionUso)&&(identical(other.requiereApoyoAuxiliar, requiereApoyoAuxiliar) || other.requiereApoyoAuxiliar == requiereApoyoAuxiliar)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.updatedAt, updatedAt) || other.updatedAt == updatedAt)&&(identical(other.usuario, usuario) || other.usuario == usuario)&&(identical(other.laboratorio, laboratorio) || other.laboratorio == laboratorio)&&const DeepCollectionEquality().equals(other.recursoIds, recursoIds)&&const DeepCollectionEquality().equals(other.recursos, recursos)&&const DeepCollectionEquality().equals(other.espacioIds, espacioIds)&&const DeepCollectionEquality().equals(other.espacios, espacios)&&const DeepCollectionEquality().equals(other.acompanantes, acompanantes));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hashAll([runtimeType,id,usuarioId,laboratorioId,fecha,horaInicio,horaFin,estado,asistentes,tipo,tipoReservaId,tipoReserva,motivoSolicitudId,motivoSolicitudCodigo,motivoSolicitudNombre,asistio,motivoRechazo,propuestaMotivo,propuestaHorarios,propuestaPor,propuestaEn,descripcion,tipoSolicitud,ubicacionUso,requiereApoyoAuxiliar,createdAt,updatedAt,usuario,laboratorio,const DeepCollectionEquality().hash(recursoIds),const DeepCollectionEquality().hash(recursos),const DeepCollectionEquality().hash(espacioIds),const DeepCollectionEquality().hash(espacios),const DeepCollectionEquality().hash(acompanantes)]);

@override
String toString() {
  return 'Reserva(id: $id, usuarioId: $usuarioId, laboratorioId: $laboratorioId, fecha: $fecha, horaInicio: $horaInicio, horaFin: $horaFin, estado: $estado, asistentes: $asistentes, tipo: $tipo, tipoReservaId: $tipoReservaId, tipoReserva: $tipoReserva, motivoSolicitudId: $motivoSolicitudId, motivoSolicitudCodigo: $motivoSolicitudCodigo, motivoSolicitudNombre: $motivoSolicitudNombre, asistio: $asistio, motivoRechazo: $motivoRechazo, propuestaMotivo: $propuestaMotivo, propuestaHorarios: $propuestaHorarios, propuestaPor: $propuestaPor, propuestaEn: $propuestaEn, descripcion: $descripcion, tipoSolicitud: $tipoSolicitud, ubicacionUso: $ubicacionUso, requiereApoyoAuxiliar: $requiereApoyoAuxiliar, createdAt: $createdAt, updatedAt: $updatedAt, usuario: $usuario, laboratorio: $laboratorio, recursoIds: $recursoIds, recursos: $recursos, espacioIds: $espacioIds, espacios: $espacios, acompanantes: $acompanantes)';
}


}

/// @nodoc
abstract mixin class $ReservaCopyWith<$Res>  {
  factory $ReservaCopyWith(Reserva value, $Res Function(Reserva) _then) = _$ReservaCopyWithImpl;
@useResult
$Res call({
 int id, int usuarioId, int laboratorioId, String fecha, String horaInicio, String horaFin, EstadoReserva estado, int asistentes, TipoReserva? tipo, int? tipoReservaId, TipoReservaReserva? tipoReserva, int? motivoSolicitudId, String? motivoSolicitudCodigo, String? motivoSolicitudNombre, bool? asistio, String? motivoRechazo, String? propuestaMotivo, String? propuestaHorarios, String? propuestaPor, String? propuestaEn, String? descripcion, TipoSolicitud tipoSolicitud, String? ubicacionUso, bool requiereApoyoAuxiliar, String createdAt, String updatedAt, UsuarioReserva usuario, LaboratorioReserva laboratorio, List<int> recursoIds, List<RecursoReserva> recursos, List<int> espacioIds, List<EspacioReserva> espacios, List<ReservaAcompanante> acompanantes
});


$TipoReservaReservaCopyWith<$Res>? get tipoReserva;$UsuarioReservaCopyWith<$Res> get usuario;$LaboratorioReservaCopyWith<$Res> get laboratorio;

}
/// @nodoc
class _$ReservaCopyWithImpl<$Res>
    implements $ReservaCopyWith<$Res> {
  _$ReservaCopyWithImpl(this._self, this._then);

  final Reserva _self;
  final $Res Function(Reserva) _then;

/// Create a copy of Reserva
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? usuarioId = null,Object? laboratorioId = null,Object? fecha = null,Object? horaInicio = null,Object? horaFin = null,Object? estado = null,Object? asistentes = null,Object? tipo = freezed,Object? tipoReservaId = freezed,Object? tipoReserva = freezed,Object? motivoSolicitudId = freezed,Object? motivoSolicitudCodigo = freezed,Object? motivoSolicitudNombre = freezed,Object? asistio = freezed,Object? motivoRechazo = freezed,Object? propuestaMotivo = freezed,Object? propuestaHorarios = freezed,Object? propuestaPor = freezed,Object? propuestaEn = freezed,Object? descripcion = freezed,Object? tipoSolicitud = null,Object? ubicacionUso = freezed,Object? requiereApoyoAuxiliar = null,Object? createdAt = null,Object? updatedAt = null,Object? usuario = null,Object? laboratorio = null,Object? recursoIds = null,Object? recursos = null,Object? espacioIds = null,Object? espacios = null,Object? acompanantes = null,}) {
  return _then(Reserva(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,usuarioId: null == usuarioId ? _self.usuarioId : usuarioId // ignore: cast_nullable_to_non_nullable
as int,laboratorioId: null == laboratorioId ? _self.laboratorioId : laboratorioId // ignore: cast_nullable_to_non_nullable
as int,fecha: null == fecha ? _self.fecha : fecha // ignore: cast_nullable_to_non_nullable
as String,horaInicio: null == horaInicio ? _self.horaInicio : horaInicio // ignore: cast_nullable_to_non_nullable
as String,horaFin: null == horaFin ? _self.horaFin : horaFin // ignore: cast_nullable_to_non_nullable
as String,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as EstadoReserva,asistentes: null == asistentes ? _self.asistentes : asistentes // ignore: cast_nullable_to_non_nullable
as int,tipo: freezed == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as TipoReserva?,tipoReservaId: freezed == tipoReservaId ? _self.tipoReservaId : tipoReservaId // ignore: cast_nullable_to_non_nullable
as int?,tipoReserva: freezed == tipoReserva ? _self.tipoReserva : tipoReserva // ignore: cast_nullable_to_non_nullable
as TipoReservaReserva?,motivoSolicitudId: freezed == motivoSolicitudId ? _self.motivoSolicitudId : motivoSolicitudId // ignore: cast_nullable_to_non_nullable
as int?,motivoSolicitudCodigo: freezed == motivoSolicitudCodigo ? _self.motivoSolicitudCodigo : motivoSolicitudCodigo // ignore: cast_nullable_to_non_nullable
as String?,motivoSolicitudNombre: freezed == motivoSolicitudNombre ? _self.motivoSolicitudNombre : motivoSolicitudNombre // ignore: cast_nullable_to_non_nullable
as String?,asistio: freezed == asistio ? _self.asistio : asistio // ignore: cast_nullable_to_non_nullable
as bool?,motivoRechazo: freezed == motivoRechazo ? _self.motivoRechazo : motivoRechazo // ignore: cast_nullable_to_non_nullable
as String?,propuestaMotivo: freezed == propuestaMotivo ? _self.propuestaMotivo : propuestaMotivo // ignore: cast_nullable_to_non_nullable
as String?,propuestaHorarios: freezed == propuestaHorarios ? _self.propuestaHorarios : propuestaHorarios // ignore: cast_nullable_to_non_nullable
as String?,propuestaPor: freezed == propuestaPor ? _self.propuestaPor : propuestaPor // ignore: cast_nullable_to_non_nullable
as String?,propuestaEn: freezed == propuestaEn ? _self.propuestaEn : propuestaEn // ignore: cast_nullable_to_non_nullable
as String?,descripcion: freezed == descripcion ? _self.descripcion : descripcion // ignore: cast_nullable_to_non_nullable
as String?,tipoSolicitud: null == tipoSolicitud ? _self.tipoSolicitud : tipoSolicitud // ignore: cast_nullable_to_non_nullable
as TipoSolicitud,ubicacionUso: freezed == ubicacionUso ? _self.ubicacionUso : ubicacionUso // ignore: cast_nullable_to_non_nullable
as String?,requiereApoyoAuxiliar: null == requiereApoyoAuxiliar ? _self.requiereApoyoAuxiliar : requiereApoyoAuxiliar // ignore: cast_nullable_to_non_nullable
as bool,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as String,usuario: null == usuario ? _self.usuario : usuario // ignore: cast_nullable_to_non_nullable
as UsuarioReserva,laboratorio: null == laboratorio ? _self.laboratorio : laboratorio // ignore: cast_nullable_to_non_nullable
as LaboratorioReserva,recursoIds: null == recursoIds ? _self.recursoIds : recursoIds // ignore: cast_nullable_to_non_nullable
as List<int>,recursos: null == recursos ? _self.recursos : recursos // ignore: cast_nullable_to_non_nullable
as List<RecursoReserva>,espacioIds: null == espacioIds ? _self.espacioIds : espacioIds // ignore: cast_nullable_to_non_nullable
as List<int>,espacios: null == espacios ? _self.espacios : espacios // ignore: cast_nullable_to_non_nullable
as List<EspacioReserva>,acompanantes: null == acompanantes ? _self.acompanantes : acompanantes // ignore: cast_nullable_to_non_nullable
as List<ReservaAcompanante>,
  ));
}
/// Create a copy of Reserva
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$TipoReservaReservaCopyWith<$Res>? get tipoReserva {
    if (_self.tipoReserva == null) {
    return null;
  }

  return $TipoReservaReservaCopyWith<$Res>(_self.tipoReserva!, (value) {
    return _then(_self.copyWith(tipoReserva: value));
  });
}/// Create a copy of Reserva
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$UsuarioReservaCopyWith<$Res> get usuario {
  
  return $UsuarioReservaCopyWith<$Res>(_self.usuario, (value) {
    return _then(_self.copyWith(usuario: value));
  });
}/// Create a copy of Reserva
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$LaboratorioReservaCopyWith<$Res> get laboratorio {
  
  return $LaboratorioReservaCopyWith<$Res>(_self.laboratorio, (value) {
    return _then(_self.copyWith(laboratorio: value));
  });
}
}


/// Adds pattern-matching-related methods to [Reserva].
extension ReservaPatterns on Reserva {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Reserva value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Reserva() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Reserva value)  $default,){
final _that = this;
switch (_that) {
case _Reserva():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Reserva value)?  $default,){
final _that = this;
switch (_that) {
case _Reserva() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  int usuarioId,  int laboratorioId,  String fecha,  String horaInicio,  String horaFin,  EstadoReserva estado,  int asistentes,  TipoReserva? tipo,  int? tipoReservaId,  TipoReservaReserva? tipoReserva,  int? motivoSolicitudId,  String? motivoSolicitudCodigo,  String? motivoSolicitudNombre,  bool? asistio,  String? motivoRechazo,  String? propuestaMotivo,  String? propuestaHorarios,  String? propuestaPor,  String? propuestaEn,  String? descripcion,  TipoSolicitud tipoSolicitud,  String? ubicacionUso,  bool requiereApoyoAuxiliar,  String createdAt,  String updatedAt,  UsuarioReserva usuario,  LaboratorioReserva laboratorio,  List<int> recursoIds,  List<RecursoReserva> recursos,  List<int> espacioIds,  List<EspacioReserva> espacios,  List<ReservaAcompanante> acompanantes)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Reserva() when $default != null:
return $default(_that.id,_that.usuarioId,_that.laboratorioId,_that.fecha,_that.horaInicio,_that.horaFin,_that.estado,_that.asistentes,_that.tipo,_that.tipoReservaId,_that.tipoReserva,_that.motivoSolicitudId,_that.motivoSolicitudCodigo,_that.motivoSolicitudNombre,_that.asistio,_that.motivoRechazo,_that.propuestaMotivo,_that.propuestaHorarios,_that.propuestaPor,_that.propuestaEn,_that.descripcion,_that.tipoSolicitud,_that.ubicacionUso,_that.requiereApoyoAuxiliar,_that.createdAt,_that.updatedAt,_that.usuario,_that.laboratorio,_that.recursoIds,_that.recursos,_that.espacioIds,_that.espacios,_that.acompanantes);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  int usuarioId,  int laboratorioId,  String fecha,  String horaInicio,  String horaFin,  EstadoReserva estado,  int asistentes,  TipoReserva? tipo,  int? tipoReservaId,  TipoReservaReserva? tipoReserva,  int? motivoSolicitudId,  String? motivoSolicitudCodigo,  String? motivoSolicitudNombre,  bool? asistio,  String? motivoRechazo,  String? propuestaMotivo,  String? propuestaHorarios,  String? propuestaPor,  String? propuestaEn,  String? descripcion,  TipoSolicitud tipoSolicitud,  String? ubicacionUso,  bool requiereApoyoAuxiliar,  String createdAt,  String updatedAt,  UsuarioReserva usuario,  LaboratorioReserva laboratorio,  List<int> recursoIds,  List<RecursoReserva> recursos,  List<int> espacioIds,  List<EspacioReserva> espacios,  List<ReservaAcompanante> acompanantes)  $default,) {final _that = this;
switch (_that) {
case _Reserva():
return $default(_that.id,_that.usuarioId,_that.laboratorioId,_that.fecha,_that.horaInicio,_that.horaFin,_that.estado,_that.asistentes,_that.tipo,_that.tipoReservaId,_that.tipoReserva,_that.motivoSolicitudId,_that.motivoSolicitudCodigo,_that.motivoSolicitudNombre,_that.asistio,_that.motivoRechazo,_that.propuestaMotivo,_that.propuestaHorarios,_that.propuestaPor,_that.propuestaEn,_that.descripcion,_that.tipoSolicitud,_that.ubicacionUso,_that.requiereApoyoAuxiliar,_that.createdAt,_that.updatedAt,_that.usuario,_that.laboratorio,_that.recursoIds,_that.recursos,_that.espacioIds,_that.espacios,_that.acompanantes);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  int usuarioId,  int laboratorioId,  String fecha,  String horaInicio,  String horaFin,  EstadoReserva estado,  int asistentes,  TipoReserva? tipo,  int? tipoReservaId,  TipoReservaReserva? tipoReserva,  int? motivoSolicitudId,  String? motivoSolicitudCodigo,  String? motivoSolicitudNombre,  bool? asistio,  String? motivoRechazo,  String? propuestaMotivo,  String? propuestaHorarios,  String? propuestaPor,  String? propuestaEn,  String? descripcion,  TipoSolicitud tipoSolicitud,  String? ubicacionUso,  bool requiereApoyoAuxiliar,  String createdAt,  String updatedAt,  UsuarioReserva usuario,  LaboratorioReserva laboratorio,  List<int> recursoIds,  List<RecursoReserva> recursos,  List<int> espacioIds,  List<EspacioReserva> espacios,  List<ReservaAcompanante> acompanantes)?  $default,) {final _that = this;
switch (_that) {
case _Reserva() when $default != null:
return $default(_that.id,_that.usuarioId,_that.laboratorioId,_that.fecha,_that.horaInicio,_that.horaFin,_that.estado,_that.asistentes,_that.tipo,_that.tipoReservaId,_that.tipoReserva,_that.motivoSolicitudId,_that.motivoSolicitudCodigo,_that.motivoSolicitudNombre,_that.asistio,_that.motivoRechazo,_that.propuestaMotivo,_that.propuestaHorarios,_that.propuestaPor,_that.propuestaEn,_that.descripcion,_that.tipoSolicitud,_that.ubicacionUso,_that.requiereApoyoAuxiliar,_that.createdAt,_that.updatedAt,_that.usuario,_that.laboratorio,_that.recursoIds,_that.recursos,_that.espacioIds,_that.espacios,_that.acompanantes);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Reserva extends Reserva {
  const _Reserva({required this.id, required this.usuarioId, required this.laboratorioId, required this.fecha, required this.horaInicio, required this.horaFin, required this.estado, required this.asistentes, this.tipo, this.tipoReservaId, this.tipoReserva, this.motivoSolicitudId, this.motivoSolicitudCodigo, this.motivoSolicitudNombre, this.asistio, this.motivoRechazo, this.propuestaMotivo, this.propuestaHorarios, this.propuestaPor, this.propuestaEn, this.descripcion, this.tipoSolicitud = TipoSolicitud.reservaEnLaboratorio, this.ubicacionUso, this.requiereApoyoAuxiliar = false, required this.createdAt, required this.updatedAt, required this.usuario, required this.laboratorio,  List<int> recursoIds = const [],  List<RecursoReserva> recursos = const [],  List<int> espacioIds = const [],  List<EspacioReserva> espacios = const [],  List<ReservaAcompanante> acompanantes = const []}): _recursoIds = recursoIds,_recursos = recursos,_espacioIds = espacioIds,_espacios = espacios,_acompanantes = acompanantes,super._();
  factory _Reserva.fromJson(Map<String, dynamic> json) => _$ReservaFromJson(json);

@override final  int id;
@override final  int usuarioId;
@override final  int laboratorioId;
@override final  String fecha;
@override final  String horaInicio;
@override final  String horaFin;
@override final  EstadoReserva estado;
@override final  int asistentes;
@override final  TipoReserva? tipo;
@override final  int? tipoReservaId;
@override final  TipoReservaReserva? tipoReserva;
@override final  int? motivoSolicitudId;
@override final  String? motivoSolicitudCodigo;
@override final  String? motivoSolicitudNombre;
@override final  bool? asistio;
@override final  String? motivoRechazo;
@override final  String? propuestaMotivo;
@override final  String? propuestaHorarios;
@override final  String? propuestaPor;
@override final  String? propuestaEn;
@override final  String? descripcion;
@override@JsonKey() final  TipoSolicitud tipoSolicitud;
@override final  String? ubicacionUso;
@override@JsonKey() final  bool requiereApoyoAuxiliar;
@override final  String createdAt;
@override final  String updatedAt;
@override final  UsuarioReserva usuario;
@override final  LaboratorioReserva laboratorio;
 final  List<int> _recursoIds;
@override@JsonKey() List<int> get recursoIds {
  if (_recursoIds is EqualUnmodifiableListView) return _recursoIds;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_recursoIds);
}

 final  List<RecursoReserva> _recursos;
@override@JsonKey() List<RecursoReserva> get recursos {
  if (_recursos is EqualUnmodifiableListView) return _recursos;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_recursos);
}

 final  List<int> _espacioIds;
@override@JsonKey() List<int> get espacioIds {
  if (_espacioIds is EqualUnmodifiableListView) return _espacioIds;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_espacioIds);
}

 final  List<EspacioReserva> _espacios;
@override@JsonKey() List<EspacioReserva> get espacios {
  if (_espacios is EqualUnmodifiableListView) return _espacios;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_espacios);
}

 final  List<ReservaAcompanante> _acompanantes;
@override@JsonKey() List<ReservaAcompanante> get acompanantes {
  if (_acompanantes is EqualUnmodifiableListView) return _acompanantes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_acompanantes);
}


/// Create a copy of Reserva
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ReservaCopyWith<_Reserva> get copyWith => __$ReservaCopyWithImpl<_Reserva>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ReservaToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _Reserva&&(identical(other.id, id) || other.id == id)&&(identical(other.usuarioId, usuarioId) || other.usuarioId == usuarioId)&&(identical(other.laboratorioId, laboratorioId) || other.laboratorioId == laboratorioId)&&(identical(other.fecha, fecha) || other.fecha == fecha)&&(identical(other.horaInicio, horaInicio) || other.horaInicio == horaInicio)&&(identical(other.horaFin, horaFin) || other.horaFin == horaFin)&&(identical(other.estado, estado) || other.estado == estado)&&(identical(other.asistentes, asistentes) || other.asistentes == asistentes)&&(identical(other.tipo, tipo) || other.tipo == tipo)&&(identical(other.tipoReservaId, tipoReservaId) || other.tipoReservaId == tipoReservaId)&&(identical(other.tipoReserva, tipoReserva) || other.tipoReserva == tipoReserva)&&(identical(other.motivoSolicitudId, motivoSolicitudId) || other.motivoSolicitudId == motivoSolicitudId)&&(identical(other.motivoSolicitudCodigo, motivoSolicitudCodigo) || other.motivoSolicitudCodigo == motivoSolicitudCodigo)&&(identical(other.motivoSolicitudNombre, motivoSolicitudNombre) || other.motivoSolicitudNombre == motivoSolicitudNombre)&&(identical(other.asistio, asistio) || other.asistio == asistio)&&(identical(other.motivoRechazo, motivoRechazo) || other.motivoRechazo == motivoRechazo)&&(identical(other.propuestaMotivo, propuestaMotivo) || other.propuestaMotivo == propuestaMotivo)&&(identical(other.propuestaHorarios, propuestaHorarios) || other.propuestaHorarios == propuestaHorarios)&&(identical(other.propuestaPor, propuestaPor) || other.propuestaPor == propuestaPor)&&(identical(other.propuestaEn, propuestaEn) || other.propuestaEn == propuestaEn)&&(identical(other.descripcion, descripcion) || other.descripcion == descripcion)&&(identical(other.tipoSolicitud, tipoSolicitud) || other.tipoSolicitud == tipoSolicitud)&&(identical(other.ubicacionUso, ubicacionUso) || other.ubicacionUso == ubicacionUso)&&(identical(other.requiereApoyoAuxiliar, requiereApoyoAuxiliar) || other.requiereApoyoAuxiliar == requiereApoyoAuxiliar)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.updatedAt, updatedAt) || other.updatedAt == updatedAt)&&(identical(other.usuario, usuario) || other.usuario == usuario)&&(identical(other.laboratorio, laboratorio) || other.laboratorio == laboratorio)&&const DeepCollectionEquality().equals(other._recursoIds, _recursoIds)&&const DeepCollectionEquality().equals(other._recursos, _recursos)&&const DeepCollectionEquality().equals(other._espacioIds, _espacioIds)&&const DeepCollectionEquality().equals(other._espacios, _espacios)&&const DeepCollectionEquality().equals(other._acompanantes, _acompanantes));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hashAll([runtimeType,id,usuarioId,laboratorioId,fecha,horaInicio,horaFin,estado,asistentes,tipo,tipoReservaId,tipoReserva,motivoSolicitudId,motivoSolicitudCodigo,motivoSolicitudNombre,asistio,motivoRechazo,propuestaMotivo,propuestaHorarios,propuestaPor,propuestaEn,descripcion,tipoSolicitud,ubicacionUso,requiereApoyoAuxiliar,createdAt,updatedAt,usuario,laboratorio,const DeepCollectionEquality().hash(_recursoIds),const DeepCollectionEquality().hash(_recursos),const DeepCollectionEquality().hash(_espacioIds),const DeepCollectionEquality().hash(_espacios),const DeepCollectionEquality().hash(_acompanantes)]);

@override
String toString() {
  return 'Reserva(id: $id, usuarioId: $usuarioId, laboratorioId: $laboratorioId, fecha: $fecha, horaInicio: $horaInicio, horaFin: $horaFin, estado: $estado, asistentes: $asistentes, tipo: $tipo, tipoReservaId: $tipoReservaId, tipoReserva: $tipoReserva, motivoSolicitudId: $motivoSolicitudId, motivoSolicitudCodigo: $motivoSolicitudCodigo, motivoSolicitudNombre: $motivoSolicitudNombre, asistio: $asistio, motivoRechazo: $motivoRechazo, propuestaMotivo: $propuestaMotivo, propuestaHorarios: $propuestaHorarios, propuestaPor: $propuestaPor, propuestaEn: $propuestaEn, descripcion: $descripcion, tipoSolicitud: $tipoSolicitud, ubicacionUso: $ubicacionUso, requiereApoyoAuxiliar: $requiereApoyoAuxiliar, createdAt: $createdAt, updatedAt: $updatedAt, usuario: $usuario, laboratorio: $laboratorio, recursoIds: $recursoIds, recursos: $recursos, espacioIds: $espacioIds, espacios: $espacios, acompanantes: $acompanantes)';
}


}

/// @nodoc
abstract mixin class _$ReservaCopyWith<$Res> implements $ReservaCopyWith<$Res> {
  factory _$ReservaCopyWith(_Reserva value, $Res Function(_Reserva) _then) = __$ReservaCopyWithImpl;
@override @useResult
$Res call({
 int id, int usuarioId, int laboratorioId, String fecha, String horaInicio, String horaFin, EstadoReserva estado, int asistentes, TipoReserva? tipo, int? tipoReservaId, TipoReservaReserva? tipoReserva, int? motivoSolicitudId, String? motivoSolicitudCodigo, String? motivoSolicitudNombre, bool? asistio, String? motivoRechazo, String? propuestaMotivo, String? propuestaHorarios, String? propuestaPor, String? propuestaEn, String? descripcion, TipoSolicitud tipoSolicitud, String? ubicacionUso, bool requiereApoyoAuxiliar, String createdAt, String updatedAt, UsuarioReserva usuario, LaboratorioReserva laboratorio, List<int> recursoIds, List<RecursoReserva> recursos, List<int> espacioIds, List<EspacioReserva> espacios, List<ReservaAcompanante> acompanantes
});


@override $TipoReservaReservaCopyWith<$Res>? get tipoReserva;@override $UsuarioReservaCopyWith<$Res> get usuario;@override $LaboratorioReservaCopyWith<$Res> get laboratorio;

}
/// @nodoc
class __$ReservaCopyWithImpl<$Res>
    implements _$ReservaCopyWith<$Res> {
  __$ReservaCopyWithImpl(this._self, this._then);

  final _Reserva _self;
  final $Res Function(_Reserva) _then;

/// Create a copy of Reserva
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? usuarioId = null,Object? laboratorioId = null,Object? fecha = null,Object? horaInicio = null,Object? horaFin = null,Object? estado = null,Object? asistentes = null,Object? tipo = freezed,Object? tipoReservaId = freezed,Object? tipoReserva = freezed,Object? motivoSolicitudId = freezed,Object? motivoSolicitudCodigo = freezed,Object? motivoSolicitudNombre = freezed,Object? asistio = freezed,Object? motivoRechazo = freezed,Object? propuestaMotivo = freezed,Object? propuestaHorarios = freezed,Object? propuestaPor = freezed,Object? propuestaEn = freezed,Object? descripcion = freezed,Object? tipoSolicitud = null,Object? ubicacionUso = freezed,Object? requiereApoyoAuxiliar = null,Object? createdAt = null,Object? updatedAt = null,Object? usuario = null,Object? laboratorio = null,Object? recursoIds = null,Object? recursos = null,Object? espacioIds = null,Object? espacios = null,Object? acompanantes = null,}) {
  return _then(_Reserva(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,usuarioId: null == usuarioId ? _self.usuarioId : usuarioId // ignore: cast_nullable_to_non_nullable
as int,laboratorioId: null == laboratorioId ? _self.laboratorioId : laboratorioId // ignore: cast_nullable_to_non_nullable
as int,fecha: null == fecha ? _self.fecha : fecha // ignore: cast_nullable_to_non_nullable
as String,horaInicio: null == horaInicio ? _self.horaInicio : horaInicio // ignore: cast_nullable_to_non_nullable
as String,horaFin: null == horaFin ? _self.horaFin : horaFin // ignore: cast_nullable_to_non_nullable
as String,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as EstadoReserva,asistentes: null == asistentes ? _self.asistentes : asistentes // ignore: cast_nullable_to_non_nullable
as int,tipo: freezed == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as TipoReserva?,tipoReservaId: freezed == tipoReservaId ? _self.tipoReservaId : tipoReservaId // ignore: cast_nullable_to_non_nullable
as int?,tipoReserva: freezed == tipoReserva ? _self.tipoReserva : tipoReserva // ignore: cast_nullable_to_non_nullable
as TipoReservaReserva?,motivoSolicitudId: freezed == motivoSolicitudId ? _self.motivoSolicitudId : motivoSolicitudId // ignore: cast_nullable_to_non_nullable
as int?,motivoSolicitudCodigo: freezed == motivoSolicitudCodigo ? _self.motivoSolicitudCodigo : motivoSolicitudCodigo // ignore: cast_nullable_to_non_nullable
as String?,motivoSolicitudNombre: freezed == motivoSolicitudNombre ? _self.motivoSolicitudNombre : motivoSolicitudNombre // ignore: cast_nullable_to_non_nullable
as String?,asistio: freezed == asistio ? _self.asistio : asistio // ignore: cast_nullable_to_non_nullable
as bool?,motivoRechazo: freezed == motivoRechazo ? _self.motivoRechazo : motivoRechazo // ignore: cast_nullable_to_non_nullable
as String?,propuestaMotivo: freezed == propuestaMotivo ? _self.propuestaMotivo : propuestaMotivo // ignore: cast_nullable_to_non_nullable
as String?,propuestaHorarios: freezed == propuestaHorarios ? _self.propuestaHorarios : propuestaHorarios // ignore: cast_nullable_to_non_nullable
as String?,propuestaPor: freezed == propuestaPor ? _self.propuestaPor : propuestaPor // ignore: cast_nullable_to_non_nullable
as String?,propuestaEn: freezed == propuestaEn ? _self.propuestaEn : propuestaEn // ignore: cast_nullable_to_non_nullable
as String?,descripcion: freezed == descripcion ? _self.descripcion : descripcion // ignore: cast_nullable_to_non_nullable
as String?,tipoSolicitud: null == tipoSolicitud ? _self.tipoSolicitud : tipoSolicitud // ignore: cast_nullable_to_non_nullable
as TipoSolicitud,ubicacionUso: freezed == ubicacionUso ? _self.ubicacionUso : ubicacionUso // ignore: cast_nullable_to_non_nullable
as String?,requiereApoyoAuxiliar: null == requiereApoyoAuxiliar ? _self.requiereApoyoAuxiliar : requiereApoyoAuxiliar // ignore: cast_nullable_to_non_nullable
as bool,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as String,usuario: null == usuario ? _self.usuario : usuario // ignore: cast_nullable_to_non_nullable
as UsuarioReserva,laboratorio: null == laboratorio ? _self.laboratorio : laboratorio // ignore: cast_nullable_to_non_nullable
as LaboratorioReserva,recursoIds: null == recursoIds ? _self._recursoIds : recursoIds // ignore: cast_nullable_to_non_nullable
as List<int>,recursos: null == recursos ? _self._recursos : recursos // ignore: cast_nullable_to_non_nullable
as List<RecursoReserva>,espacioIds: null == espacioIds ? _self._espacioIds : espacioIds // ignore: cast_nullable_to_non_nullable
as List<int>,espacios: null == espacios ? _self._espacios : espacios // ignore: cast_nullable_to_non_nullable
as List<EspacioReserva>,acompanantes: null == acompanantes ? _self._acompanantes : acompanantes // ignore: cast_nullable_to_non_nullable
as List<ReservaAcompanante>,
  ));
}

/// Create a copy of Reserva
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$TipoReservaReservaCopyWith<$Res>? get tipoReserva {
    if (_self.tipoReserva == null) {
    return null;
  }

  return $TipoReservaReservaCopyWith<$Res>(_self.tipoReserva!, (value) {
    return _then(_self.copyWith(tipoReserva: value));
  });
}/// Create a copy of Reserva
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$UsuarioReservaCopyWith<$Res> get usuario {
  
  return $UsuarioReservaCopyWith<$Res>(_self.usuario, (value) {
    return _then(_self.copyWith(usuario: value));
  });
}/// Create a copy of Reserva
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$LaboratorioReservaCopyWith<$Res> get laboratorio {
  
  return $LaboratorioReservaCopyWith<$Res>(_self.laboratorio, (value) {
    return _then(_self.copyWith(laboratorio: value));
  });
}
}

// dart format on
