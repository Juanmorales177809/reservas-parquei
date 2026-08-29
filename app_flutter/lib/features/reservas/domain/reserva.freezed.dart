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
mixin _$EspacioReserva {

 int get id; String get nombre; int? get capacidad; EstadoEntidad get estado;
/// Create a copy of EspacioReserva
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$EspacioReservaCopyWith<EspacioReserva> get copyWith => _$EspacioReservaCopyWithImpl<EspacioReserva>(this as EspacioReserva, _$identity);

  /// Serializes this EspacioReserva to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is EspacioReserva&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.capacidad, capacidad) || other.capacidad == capacidad)&&(identical(other.estado, estado) || other.estado == estado));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,capacidad,estado);

@override
String toString() {
  return 'EspacioReserva(id: $id, nombre: $nombre, capacidad: $capacidad, estado: $estado)';
}


}

/// @nodoc
abstract mixin class $EspacioReservaCopyWith<$Res>  {
  factory $EspacioReservaCopyWith(EspacioReserva value, $Res Function(EspacioReserva) _then) = _$EspacioReservaCopyWithImpl;
@useResult
$Res call({
 int id, String nombre, int? capacidad, EstadoEntidad estado
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
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? nombre = null,Object? capacidad = freezed,Object? estado = null,}) {
  return _then(EspacioReserva(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,capacidad: freezed == capacidad ? _self.capacidad : capacidad // ignore: cast_nullable_to_non_nullable
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  String nombre,  int? capacidad,  EstadoEntidad estado)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _EspacioReserva() when $default != null:
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
case _EspacioReserva():
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
case _EspacioReserva() when $default != null:
return $default(_that.id,_that.nombre,_that.capacidad,_that.estado);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _EspacioReserva implements EspacioReserva {
  const _EspacioReserva({required this.id, required this.nombre, this.capacidad, required this.estado});
  factory _EspacioReserva.fromJson(Map<String, dynamic> json) => _$EspacioReservaFromJson(json);

@override final  int id;
@override final  String nombre;
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
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _EspacioReserva&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.capacidad, capacidad) || other.capacidad == capacidad)&&(identical(other.estado, estado) || other.estado == estado));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,capacidad,estado);

@override
String toString() {
  return 'EspacioReserva(id: $id, nombre: $nombre, capacidad: $capacidad, estado: $estado)';
}


}

/// @nodoc
abstract mixin class _$EspacioReservaCopyWith<$Res> implements $EspacioReservaCopyWith<$Res> {
  factory _$EspacioReservaCopyWith(_EspacioReserva value, $Res Function(_EspacioReserva) _then) = __$EspacioReservaCopyWithImpl;
@override @useResult
$Res call({
 int id, String nombre, int? capacidad, EstadoEntidad estado
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
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? nombre = null,Object? capacidad = freezed,Object? estado = null,}) {
  return _then(_EspacioReserva(
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

 int get id; String get nombre; int? get capacidad; EstadoEntidad get estado; EspacioReserva get espacio;
/// Create a copy of RecursoReserva
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RecursoReservaCopyWith<RecursoReserva> get copyWith => _$RecursoReservaCopyWithImpl<RecursoReserva>(this as RecursoReserva, _$identity);

  /// Serializes this RecursoReserva to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is RecursoReserva&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.capacidad, capacidad) || other.capacidad == capacidad)&&(identical(other.estado, estado) || other.estado == estado)&&(identical(other.espacio, espacio) || other.espacio == espacio));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,capacidad,estado,espacio);

@override
String toString() {
  return 'RecursoReserva(id: $id, nombre: $nombre, capacidad: $capacidad, estado: $estado, espacio: $espacio)';
}


}

/// @nodoc
abstract mixin class $RecursoReservaCopyWith<$Res>  {
  factory $RecursoReservaCopyWith(RecursoReserva value, $Res Function(RecursoReserva) _then) = _$RecursoReservaCopyWithImpl;
@useResult
$Res call({
 int id, String nombre, int? capacidad, EstadoEntidad estado, EspacioReserva espacio
});


$EspacioReservaCopyWith<$Res> get espacio;

}
/// @nodoc
class _$RecursoReservaCopyWithImpl<$Res>
    implements $RecursoReservaCopyWith<$Res> {
  _$RecursoReservaCopyWithImpl(this._self, this._then);

  final RecursoReserva _self;
  final $Res Function(RecursoReserva) _then;

/// Create a copy of RecursoReserva
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? nombre = null,Object? capacidad = freezed,Object? estado = null,Object? espacio = null,}) {
  return _then(RecursoReserva(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,capacidad: freezed == capacidad ? _self.capacidad : capacidad // ignore: cast_nullable_to_non_nullable
as int?,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as EstadoEntidad,espacio: null == espacio ? _self.espacio : espacio // ignore: cast_nullable_to_non_nullable
as EspacioReserva,
  ));
}
/// Create a copy of RecursoReserva
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$EspacioReservaCopyWith<$Res> get espacio {
  
  return $EspacioReservaCopyWith<$Res>(_self.espacio, (value) {
    return _then(_self.copyWith(espacio: value));
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  String nombre,  int? capacidad,  EstadoEntidad estado,  EspacioReserva espacio)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _RecursoReserva() when $default != null:
return $default(_that.id,_that.nombre,_that.capacidad,_that.estado,_that.espacio);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  String nombre,  int? capacidad,  EstadoEntidad estado,  EspacioReserva espacio)  $default,) {final _that = this;
switch (_that) {
case _RecursoReserva():
return $default(_that.id,_that.nombre,_that.capacidad,_that.estado,_that.espacio);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  String nombre,  int? capacidad,  EstadoEntidad estado,  EspacioReserva espacio)?  $default,) {final _that = this;
switch (_that) {
case _RecursoReserva() when $default != null:
return $default(_that.id,_that.nombre,_that.capacidad,_that.estado,_that.espacio);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _RecursoReserva implements RecursoReserva {
  const _RecursoReserva({required this.id, required this.nombre, this.capacidad, required this.estado, required this.espacio});
  factory _RecursoReserva.fromJson(Map<String, dynamic> json) => _$RecursoReservaFromJson(json);

@override final  int id;
@override final  String nombre;
@override final  int? capacidad;
@override final  EstadoEntidad estado;
@override final  EspacioReserva espacio;

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
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _RecursoReserva&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.capacidad, capacidad) || other.capacidad == capacidad)&&(identical(other.estado, estado) || other.estado == estado)&&(identical(other.espacio, espacio) || other.espacio == espacio));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,capacidad,estado,espacio);

@override
String toString() {
  return 'RecursoReserva(id: $id, nombre: $nombre, capacidad: $capacidad, estado: $estado, espacio: $espacio)';
}


}

/// @nodoc
abstract mixin class _$RecursoReservaCopyWith<$Res> implements $RecursoReservaCopyWith<$Res> {
  factory _$RecursoReservaCopyWith(_RecursoReserva value, $Res Function(_RecursoReserva) _then) = __$RecursoReservaCopyWithImpl;
@override @useResult
$Res call({
 int id, String nombre, int? capacidad, EstadoEntidad estado, EspacioReserva espacio
});


@override $EspacioReservaCopyWith<$Res> get espacio;

}
/// @nodoc
class __$RecursoReservaCopyWithImpl<$Res>
    implements _$RecursoReservaCopyWith<$Res> {
  __$RecursoReservaCopyWithImpl(this._self, this._then);

  final _RecursoReserva _self;
  final $Res Function(_RecursoReserva) _then;

/// Create a copy of RecursoReserva
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? nombre = null,Object? capacidad = freezed,Object? estado = null,Object? espacio = null,}) {
  return _then(_RecursoReserva(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,capacidad: freezed == capacidad ? _self.capacidad : capacidad // ignore: cast_nullable_to_non_nullable
as int?,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as EstadoEntidad,espacio: null == espacio ? _self.espacio : espacio // ignore: cast_nullable_to_non_nullable
as EspacioReserva,
  ));
}

/// Create a copy of RecursoReserva
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$EspacioReservaCopyWith<$Res> get espacio {
  
  return $EspacioReservaCopyWith<$Res>(_self.espacio, (value) {
    return _then(_self.copyWith(espacio: value));
  });
}
}


/// @nodoc
mixin _$ZonaReserva {

 int get id; String get nombre; int get espacioId; String? get descripcion; int? get capacidad; EstadoEntidad get estado;
/// Create a copy of ZonaReserva
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ZonaReservaCopyWith<ZonaReserva> get copyWith => _$ZonaReservaCopyWithImpl<ZonaReserva>(this as ZonaReserva, _$identity);

  /// Serializes this ZonaReserva to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ZonaReserva&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.espacioId, espacioId) || other.espacioId == espacioId)&&(identical(other.descripcion, descripcion) || other.descripcion == descripcion)&&(identical(other.capacidad, capacidad) || other.capacidad == capacidad)&&(identical(other.estado, estado) || other.estado == estado));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,espacioId,descripcion,capacidad,estado);

@override
String toString() {
  return 'ZonaReserva(id: $id, nombre: $nombre, espacioId: $espacioId, descripcion: $descripcion, capacidad: $capacidad, estado: $estado)';
}


}

/// @nodoc
abstract mixin class $ZonaReservaCopyWith<$Res>  {
  factory $ZonaReservaCopyWith(ZonaReserva value, $Res Function(ZonaReserva) _then) = _$ZonaReservaCopyWithImpl;
@useResult
$Res call({
 int id, String nombre, int espacioId, String? descripcion, int? capacidad, EstadoEntidad estado
});




}
/// @nodoc
class _$ZonaReservaCopyWithImpl<$Res>
    implements $ZonaReservaCopyWith<$Res> {
  _$ZonaReservaCopyWithImpl(this._self, this._then);

  final ZonaReserva _self;
  final $Res Function(ZonaReserva) _then;

/// Create a copy of ZonaReserva
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? nombre = null,Object? espacioId = null,Object? descripcion = freezed,Object? capacidad = freezed,Object? estado = null,}) {
  return _then(ZonaReserva(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,espacioId: null == espacioId ? _self.espacioId : espacioId // ignore: cast_nullable_to_non_nullable
as int,descripcion: freezed == descripcion ? _self.descripcion : descripcion // ignore: cast_nullable_to_non_nullable
as String?,capacidad: freezed == capacidad ? _self.capacidad : capacidad // ignore: cast_nullable_to_non_nullable
as int?,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as EstadoEntidad,
  ));
}

}


/// Adds pattern-matching-related methods to [ZonaReserva].
extension ZonaReservaPatterns on ZonaReserva {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ZonaReserva value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ZonaReserva() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ZonaReserva value)  $default,){
final _that = this;
switch (_that) {
case _ZonaReserva():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ZonaReserva value)?  $default,){
final _that = this;
switch (_that) {
case _ZonaReserva() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  String nombre,  int espacioId,  String? descripcion,  int? capacidad,  EstadoEntidad estado)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ZonaReserva() when $default != null:
return $default(_that.id,_that.nombre,_that.espacioId,_that.descripcion,_that.capacidad,_that.estado);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  String nombre,  int espacioId,  String? descripcion,  int? capacidad,  EstadoEntidad estado)  $default,) {final _that = this;
switch (_that) {
case _ZonaReserva():
return $default(_that.id,_that.nombre,_that.espacioId,_that.descripcion,_that.capacidad,_that.estado);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  String nombre,  int espacioId,  String? descripcion,  int? capacidad,  EstadoEntidad estado)?  $default,) {final _that = this;
switch (_that) {
case _ZonaReserva() when $default != null:
return $default(_that.id,_that.nombre,_that.espacioId,_that.descripcion,_that.capacidad,_that.estado);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ZonaReserva implements ZonaReserva {
  const _ZonaReserva({required this.id, required this.nombre, required this.espacioId, this.descripcion, this.capacidad, required this.estado});
  factory _ZonaReserva.fromJson(Map<String, dynamic> json) => _$ZonaReservaFromJson(json);

@override final  int id;
@override final  String nombre;
@override final  int espacioId;
@override final  String? descripcion;
@override final  int? capacidad;
@override final  EstadoEntidad estado;

/// Create a copy of ZonaReserva
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ZonaReservaCopyWith<_ZonaReserva> get copyWith => __$ZonaReservaCopyWithImpl<_ZonaReserva>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ZonaReservaToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ZonaReserva&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.espacioId, espacioId) || other.espacioId == espacioId)&&(identical(other.descripcion, descripcion) || other.descripcion == descripcion)&&(identical(other.capacidad, capacidad) || other.capacidad == capacidad)&&(identical(other.estado, estado) || other.estado == estado));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,espacioId,descripcion,capacidad,estado);

@override
String toString() {
  return 'ZonaReserva(id: $id, nombre: $nombre, espacioId: $espacioId, descripcion: $descripcion, capacidad: $capacidad, estado: $estado)';
}


}

/// @nodoc
abstract mixin class _$ZonaReservaCopyWith<$Res> implements $ZonaReservaCopyWith<$Res> {
  factory _$ZonaReservaCopyWith(_ZonaReserva value, $Res Function(_ZonaReserva) _then) = __$ZonaReservaCopyWithImpl;
@override @useResult
$Res call({
 int id, String nombre, int espacioId, String? descripcion, int? capacidad, EstadoEntidad estado
});




}
/// @nodoc
class __$ZonaReservaCopyWithImpl<$Res>
    implements _$ZonaReservaCopyWith<$Res> {
  __$ZonaReservaCopyWithImpl(this._self, this._then);

  final _ZonaReserva _self;
  final $Res Function(_ZonaReserva) _then;

/// Create a copy of ZonaReserva
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? nombre = null,Object? espacioId = null,Object? descripcion = freezed,Object? capacidad = freezed,Object? estado = null,}) {
  return _then(_ZonaReserva(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,espacioId: null == espacioId ? _self.espacioId : espacioId // ignore: cast_nullable_to_non_nullable
as int,descripcion: freezed == descripcion ? _self.descripcion : descripcion // ignore: cast_nullable_to_non_nullable
as String?,capacidad: freezed == capacidad ? _self.capacidad : capacidad // ignore: cast_nullable_to_non_nullable
as int?,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as EstadoEntidad,
  ));
}


}


/// @nodoc
mixin _$EnsayoReserva {

 int get id; String get nombre; int get zonaId; EstadoEntidad get estado;
/// Create a copy of EnsayoReserva
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$EnsayoReservaCopyWith<EnsayoReserva> get copyWith => _$EnsayoReservaCopyWithImpl<EnsayoReserva>(this as EnsayoReserva, _$identity);

  /// Serializes this EnsayoReserva to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is EnsayoReserva&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.zonaId, zonaId) || other.zonaId == zonaId)&&(identical(other.estado, estado) || other.estado == estado));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,zonaId,estado);

@override
String toString() {
  return 'EnsayoReserva(id: $id, nombre: $nombre, zonaId: $zonaId, estado: $estado)';
}


}

/// @nodoc
abstract mixin class $EnsayoReservaCopyWith<$Res>  {
  factory $EnsayoReservaCopyWith(EnsayoReserva value, $Res Function(EnsayoReserva) _then) = _$EnsayoReservaCopyWithImpl;
@useResult
$Res call({
 int id, String nombre, int zonaId, EstadoEntidad estado
});




}
/// @nodoc
class _$EnsayoReservaCopyWithImpl<$Res>
    implements $EnsayoReservaCopyWith<$Res> {
  _$EnsayoReservaCopyWithImpl(this._self, this._then);

  final EnsayoReserva _self;
  final $Res Function(EnsayoReserva) _then;

/// Create a copy of EnsayoReserva
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? nombre = null,Object? zonaId = null,Object? estado = null,}) {
  return _then(EnsayoReserva(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,zonaId: null == zonaId ? _self.zonaId : zonaId // ignore: cast_nullable_to_non_nullable
as int,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as EstadoEntidad,
  ));
}

}


/// Adds pattern-matching-related methods to [EnsayoReserva].
extension EnsayoReservaPatterns on EnsayoReserva {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _EnsayoReserva value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _EnsayoReserva() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _EnsayoReserva value)  $default,){
final _that = this;
switch (_that) {
case _EnsayoReserva():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _EnsayoReserva value)?  $default,){
final _that = this;
switch (_that) {
case _EnsayoReserva() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  String nombre,  int zonaId,  EstadoEntidad estado)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _EnsayoReserva() when $default != null:
return $default(_that.id,_that.nombre,_that.zonaId,_that.estado);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  String nombre,  int zonaId,  EstadoEntidad estado)  $default,) {final _that = this;
switch (_that) {
case _EnsayoReserva():
return $default(_that.id,_that.nombre,_that.zonaId,_that.estado);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  String nombre,  int zonaId,  EstadoEntidad estado)?  $default,) {final _that = this;
switch (_that) {
case _EnsayoReserva() when $default != null:
return $default(_that.id,_that.nombre,_that.zonaId,_that.estado);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _EnsayoReserva implements EnsayoReserva {
  const _EnsayoReserva({required this.id, required this.nombre, required this.zonaId, required this.estado});
  factory _EnsayoReserva.fromJson(Map<String, dynamic> json) => _$EnsayoReservaFromJson(json);

@override final  int id;
@override final  String nombre;
@override final  int zonaId;
@override final  EstadoEntidad estado;

/// Create a copy of EnsayoReserva
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$EnsayoReservaCopyWith<_EnsayoReserva> get copyWith => __$EnsayoReservaCopyWithImpl<_EnsayoReserva>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$EnsayoReservaToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _EnsayoReserva&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.zonaId, zonaId) || other.zonaId == zonaId)&&(identical(other.estado, estado) || other.estado == estado));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,zonaId,estado);

@override
String toString() {
  return 'EnsayoReserva(id: $id, nombre: $nombre, zonaId: $zonaId, estado: $estado)';
}


}

/// @nodoc
abstract mixin class _$EnsayoReservaCopyWith<$Res> implements $EnsayoReservaCopyWith<$Res> {
  factory _$EnsayoReservaCopyWith(_EnsayoReserva value, $Res Function(_EnsayoReserva) _then) = __$EnsayoReservaCopyWithImpl;
@override @useResult
$Res call({
 int id, String nombre, int zonaId, EstadoEntidad estado
});




}
/// @nodoc
class __$EnsayoReservaCopyWithImpl<$Res>
    implements _$EnsayoReservaCopyWith<$Res> {
  __$EnsayoReservaCopyWithImpl(this._self, this._then);

  final _EnsayoReserva _self;
  final $Res Function(_EnsayoReserva) _then;

/// Create a copy of EnsayoReserva
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? nombre = null,Object? zonaId = null,Object? estado = null,}) {
  return _then(_EnsayoReserva(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,zonaId: null == zonaId ? _self.zonaId : zonaId // ignore: cast_nullable_to_non_nullable
as int,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as EstadoEntidad,
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

 int get id; int get usuarioId; int get espacioId; String get fecha; String get horaInicio; String get horaFin; EstadoReserva get estado; int get asistentes; TipoReserva? get tipo; bool? get asistio; String? get motivoRechazo; String? get descripcion; TipoSolicitud get tipoSolicitud; String? get ubicacionUso; bool get requiereApoyoAuxiliar; String get createdAt; String get updatedAt; UsuarioReserva get usuario; EspacioReserva get espacio; String? get serieId; List<int> get recursoIds; List<RecursoReserva> get recursos; List<int> get zonaIds; List<ZonaReserva> get zonas; List<int> get ensayoIds; List<EnsayoReserva> get ensayos; List<ReservaAcompanante> get acompanantes;
/// Create a copy of Reserva
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ReservaCopyWith<Reserva> get copyWith => _$ReservaCopyWithImpl<Reserva>(this as Reserva, _$identity);

  /// Serializes this Reserva to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Reserva&&(identical(other.id, id) || other.id == id)&&(identical(other.usuarioId, usuarioId) || other.usuarioId == usuarioId)&&(identical(other.espacioId, espacioId) || other.espacioId == espacioId)&&(identical(other.fecha, fecha) || other.fecha == fecha)&&(identical(other.horaInicio, horaInicio) || other.horaInicio == horaInicio)&&(identical(other.horaFin, horaFin) || other.horaFin == horaFin)&&(identical(other.estado, estado) || other.estado == estado)&&(identical(other.asistentes, asistentes) || other.asistentes == asistentes)&&(identical(other.tipo, tipo) || other.tipo == tipo)&&(identical(other.asistio, asistio) || other.asistio == asistio)&&(identical(other.motivoRechazo, motivoRechazo) || other.motivoRechazo == motivoRechazo)&&(identical(other.descripcion, descripcion) || other.descripcion == descripcion)&&(identical(other.tipoSolicitud, tipoSolicitud) || other.tipoSolicitud == tipoSolicitud)&&(identical(other.ubicacionUso, ubicacionUso) || other.ubicacionUso == ubicacionUso)&&(identical(other.requiereApoyoAuxiliar, requiereApoyoAuxiliar) || other.requiereApoyoAuxiliar == requiereApoyoAuxiliar)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.updatedAt, updatedAt) || other.updatedAt == updatedAt)&&(identical(other.usuario, usuario) || other.usuario == usuario)&&(identical(other.espacio, espacio) || other.espacio == espacio)&&(identical(other.serieId, serieId) || other.serieId == serieId)&&const DeepCollectionEquality().equals(other.recursoIds, recursoIds)&&const DeepCollectionEquality().equals(other.recursos, recursos)&&const DeepCollectionEquality().equals(other.zonaIds, zonaIds)&&const DeepCollectionEquality().equals(other.zonas, zonas)&&const DeepCollectionEquality().equals(other.ensayoIds, ensayoIds)&&const DeepCollectionEquality().equals(other.ensayos, ensayos)&&const DeepCollectionEquality().equals(other.acompanantes, acompanantes));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hashAll([runtimeType,id,usuarioId,espacioId,fecha,horaInicio,horaFin,estado,asistentes,tipo,asistio,motivoRechazo,descripcion,tipoSolicitud,ubicacionUso,requiereApoyoAuxiliar,createdAt,updatedAt,usuario,espacio,serieId,const DeepCollectionEquality().hash(recursoIds),const DeepCollectionEquality().hash(recursos),const DeepCollectionEquality().hash(zonaIds),const DeepCollectionEquality().hash(zonas),const DeepCollectionEquality().hash(ensayoIds),const DeepCollectionEquality().hash(ensayos),const DeepCollectionEquality().hash(acompanantes)]);

@override
String toString() {
  return 'Reserva(id: $id, usuarioId: $usuarioId, espacioId: $espacioId, fecha: $fecha, horaInicio: $horaInicio, horaFin: $horaFin, estado: $estado, asistentes: $asistentes, tipo: $tipo, asistio: $asistio, motivoRechazo: $motivoRechazo, descripcion: $descripcion, tipoSolicitud: $tipoSolicitud, ubicacionUso: $ubicacionUso, requiereApoyoAuxiliar: $requiereApoyoAuxiliar, createdAt: $createdAt, updatedAt: $updatedAt, usuario: $usuario, espacio: $espacio, serieId: $serieId, recursoIds: $recursoIds, recursos: $recursos, zonaIds: $zonaIds, zonas: $zonas, ensayoIds: $ensayoIds, ensayos: $ensayos, acompanantes: $acompanantes)';
}


}

/// @nodoc
abstract mixin class $ReservaCopyWith<$Res>  {
  factory $ReservaCopyWith(Reserva value, $Res Function(Reserva) _then) = _$ReservaCopyWithImpl;
@useResult
$Res call({
 int id, int usuarioId, int espacioId, String fecha, String horaInicio, String horaFin, EstadoReserva estado, int asistentes, TipoReserva? tipo, bool? asistio, String? motivoRechazo, String? descripcion, TipoSolicitud tipoSolicitud, String? ubicacionUso, bool requiereApoyoAuxiliar, String createdAt, String updatedAt, UsuarioReserva usuario, EspacioReserva espacio, String? serieId, List<int> recursoIds, List<RecursoReserva> recursos, List<int> zonaIds, List<ZonaReserva> zonas, List<int> ensayoIds, List<EnsayoReserva> ensayos, List<ReservaAcompanante> acompanantes
});


$UsuarioReservaCopyWith<$Res> get usuario;$EspacioReservaCopyWith<$Res> get espacio;

}
/// @nodoc
class _$ReservaCopyWithImpl<$Res>
    implements $ReservaCopyWith<$Res> {
  _$ReservaCopyWithImpl(this._self, this._then);

  final Reserva _self;
  final $Res Function(Reserva) _then;

/// Create a copy of Reserva
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? usuarioId = null,Object? espacioId = null,Object? fecha = null,Object? horaInicio = null,Object? horaFin = null,Object? estado = null,Object? asistentes = null,Object? tipo = freezed,Object? asistio = freezed,Object? motivoRechazo = freezed,Object? descripcion = freezed,Object? tipoSolicitud = null,Object? ubicacionUso = freezed,Object? requiereApoyoAuxiliar = null,Object? createdAt = null,Object? updatedAt = null,Object? usuario = null,Object? espacio = null,Object? serieId = freezed,Object? recursoIds = null,Object? recursos = null,Object? zonaIds = null,Object? zonas = null,Object? ensayoIds = null,Object? ensayos = null,Object? acompanantes = null,}) {
  return _then(Reserva(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,usuarioId: null == usuarioId ? _self.usuarioId : usuarioId // ignore: cast_nullable_to_non_nullable
as int,espacioId: null == espacioId ? _self.espacioId : espacioId // ignore: cast_nullable_to_non_nullable
as int,fecha: null == fecha ? _self.fecha : fecha // ignore: cast_nullable_to_non_nullable
as String,horaInicio: null == horaInicio ? _self.horaInicio : horaInicio // ignore: cast_nullable_to_non_nullable
as String,horaFin: null == horaFin ? _self.horaFin : horaFin // ignore: cast_nullable_to_non_nullable
as String,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as EstadoReserva,asistentes: null == asistentes ? _self.asistentes : asistentes // ignore: cast_nullable_to_non_nullable
as int,tipo: freezed == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as TipoReserva?,asistio: freezed == asistio ? _self.asistio : asistio // ignore: cast_nullable_to_non_nullable
as bool?,motivoRechazo: freezed == motivoRechazo ? _self.motivoRechazo : motivoRechazo // ignore: cast_nullable_to_non_nullable
as String?,descripcion: freezed == descripcion ? _self.descripcion : descripcion // ignore: cast_nullable_to_non_nullable
as String?,tipoSolicitud: null == tipoSolicitud ? _self.tipoSolicitud : tipoSolicitud // ignore: cast_nullable_to_non_nullable
as TipoSolicitud,ubicacionUso: freezed == ubicacionUso ? _self.ubicacionUso : ubicacionUso // ignore: cast_nullable_to_non_nullable
as String?,requiereApoyoAuxiliar: null == requiereApoyoAuxiliar ? _self.requiereApoyoAuxiliar : requiereApoyoAuxiliar // ignore: cast_nullable_to_non_nullable
as bool,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as String,usuario: null == usuario ? _self.usuario : usuario // ignore: cast_nullable_to_non_nullable
as UsuarioReserva,espacio: null == espacio ? _self.espacio : espacio // ignore: cast_nullable_to_non_nullable
as EspacioReserva,serieId: freezed == serieId ? _self.serieId : serieId // ignore: cast_nullable_to_non_nullable
as String?,recursoIds: null == recursoIds ? _self.recursoIds : recursoIds // ignore: cast_nullable_to_non_nullable
as List<int>,recursos: null == recursos ? _self.recursos : recursos // ignore: cast_nullable_to_non_nullable
as List<RecursoReserva>,zonaIds: null == zonaIds ? _self.zonaIds : zonaIds // ignore: cast_nullable_to_non_nullable
as List<int>,zonas: null == zonas ? _self.zonas : zonas // ignore: cast_nullable_to_non_nullable
as List<ZonaReserva>,ensayoIds: null == ensayoIds ? _self.ensayoIds : ensayoIds // ignore: cast_nullable_to_non_nullable
as List<int>,ensayos: null == ensayos ? _self.ensayos : ensayos // ignore: cast_nullable_to_non_nullable
as List<EnsayoReserva>,acompanantes: null == acompanantes ? _self.acompanantes : acompanantes // ignore: cast_nullable_to_non_nullable
as List<ReservaAcompanante>,
  ));
}
/// Create a copy of Reserva
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
$EspacioReservaCopyWith<$Res> get espacio {
  
  return $EspacioReservaCopyWith<$Res>(_self.espacio, (value) {
    return _then(_self.copyWith(espacio: value));
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  int usuarioId,  int espacioId,  String fecha,  String horaInicio,  String horaFin,  EstadoReserva estado,  int asistentes,  TipoReserva? tipo,  bool? asistio,  String? motivoRechazo,  String? descripcion,  TipoSolicitud tipoSolicitud,  String? ubicacionUso,  bool requiereApoyoAuxiliar,  String createdAt,  String updatedAt,  UsuarioReserva usuario,  EspacioReserva espacio,  String? serieId,  List<int> recursoIds,  List<RecursoReserva> recursos,  List<int> zonaIds,  List<ZonaReserva> zonas,  List<int> ensayoIds,  List<EnsayoReserva> ensayos,  List<ReservaAcompanante> acompanantes)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Reserva() when $default != null:
return $default(_that.id,_that.usuarioId,_that.espacioId,_that.fecha,_that.horaInicio,_that.horaFin,_that.estado,_that.asistentes,_that.tipo,_that.asistio,_that.motivoRechazo,_that.descripcion,_that.tipoSolicitud,_that.ubicacionUso,_that.requiereApoyoAuxiliar,_that.createdAt,_that.updatedAt,_that.usuario,_that.espacio,_that.serieId,_that.recursoIds,_that.recursos,_that.zonaIds,_that.zonas,_that.ensayoIds,_that.ensayos,_that.acompanantes);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  int usuarioId,  int espacioId,  String fecha,  String horaInicio,  String horaFin,  EstadoReserva estado,  int asistentes,  TipoReserva? tipo,  bool? asistio,  String? motivoRechazo,  String? descripcion,  TipoSolicitud tipoSolicitud,  String? ubicacionUso,  bool requiereApoyoAuxiliar,  String createdAt,  String updatedAt,  UsuarioReserva usuario,  EspacioReserva espacio,  String? serieId,  List<int> recursoIds,  List<RecursoReserva> recursos,  List<int> zonaIds,  List<ZonaReserva> zonas,  List<int> ensayoIds,  List<EnsayoReserva> ensayos,  List<ReservaAcompanante> acompanantes)  $default,) {final _that = this;
switch (_that) {
case _Reserva():
return $default(_that.id,_that.usuarioId,_that.espacioId,_that.fecha,_that.horaInicio,_that.horaFin,_that.estado,_that.asistentes,_that.tipo,_that.asistio,_that.motivoRechazo,_that.descripcion,_that.tipoSolicitud,_that.ubicacionUso,_that.requiereApoyoAuxiliar,_that.createdAt,_that.updatedAt,_that.usuario,_that.espacio,_that.serieId,_that.recursoIds,_that.recursos,_that.zonaIds,_that.zonas,_that.ensayoIds,_that.ensayos,_that.acompanantes);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  int usuarioId,  int espacioId,  String fecha,  String horaInicio,  String horaFin,  EstadoReserva estado,  int asistentes,  TipoReserva? tipo,  bool? asistio,  String? motivoRechazo,  String? descripcion,  TipoSolicitud tipoSolicitud,  String? ubicacionUso,  bool requiereApoyoAuxiliar,  String createdAt,  String updatedAt,  UsuarioReserva usuario,  EspacioReserva espacio,  String? serieId,  List<int> recursoIds,  List<RecursoReserva> recursos,  List<int> zonaIds,  List<ZonaReserva> zonas,  List<int> ensayoIds,  List<EnsayoReserva> ensayos,  List<ReservaAcompanante> acompanantes)?  $default,) {final _that = this;
switch (_that) {
case _Reserva() when $default != null:
return $default(_that.id,_that.usuarioId,_that.espacioId,_that.fecha,_that.horaInicio,_that.horaFin,_that.estado,_that.asistentes,_that.tipo,_that.asistio,_that.motivoRechazo,_that.descripcion,_that.tipoSolicitud,_that.ubicacionUso,_that.requiereApoyoAuxiliar,_that.createdAt,_that.updatedAt,_that.usuario,_that.espacio,_that.serieId,_that.recursoIds,_that.recursos,_that.zonaIds,_that.zonas,_that.ensayoIds,_that.ensayos,_that.acompanantes);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Reserva extends Reserva {
  const _Reserva({required this.id, required this.usuarioId, required this.espacioId, required this.fecha, required this.horaInicio, required this.horaFin, required this.estado, required this.asistentes, this.tipo, this.asistio, this.motivoRechazo, this.descripcion, this.tipoSolicitud = TipoSolicitud.reservaEnLaboratorio, this.ubicacionUso, this.requiereApoyoAuxiliar = false, required this.createdAt, required this.updatedAt, required this.usuario, required this.espacio, this.serieId,  List<int> recursoIds = const [],  List<RecursoReserva> recursos = const [],  List<int> zonaIds = const [],  List<ZonaReserva> zonas = const [],  List<int> ensayoIds = const [],  List<EnsayoReserva> ensayos = const [],  List<ReservaAcompanante> acompanantes = const []}): _recursoIds = recursoIds,_recursos = recursos,_zonaIds = zonaIds,_zonas = zonas,_ensayoIds = ensayoIds,_ensayos = ensayos,_acompanantes = acompanantes,super._();
  factory _Reserva.fromJson(Map<String, dynamic> json) => _$ReservaFromJson(json);

@override final  int id;
@override final  int usuarioId;
@override final  int espacioId;
@override final  String fecha;
@override final  String horaInicio;
@override final  String horaFin;
@override final  EstadoReserva estado;
@override final  int asistentes;
@override final  TipoReserva? tipo;
@override final  bool? asistio;
@override final  String? motivoRechazo;
@override final  String? descripcion;
@override@JsonKey() final  TipoSolicitud tipoSolicitud;
@override final  String? ubicacionUso;
@override@JsonKey() final  bool requiereApoyoAuxiliar;
@override final  String createdAt;
@override final  String updatedAt;
@override final  UsuarioReserva usuario;
@override final  EspacioReserva espacio;
@override final  String? serieId;
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

 final  List<int> _zonaIds;
@override@JsonKey() List<int> get zonaIds {
  if (_zonaIds is EqualUnmodifiableListView) return _zonaIds;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_zonaIds);
}

 final  List<ZonaReserva> _zonas;
@override@JsonKey() List<ZonaReserva> get zonas {
  if (_zonas is EqualUnmodifiableListView) return _zonas;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_zonas);
}

 final  List<int> _ensayoIds;
@override@JsonKey() List<int> get ensayoIds {
  if (_ensayoIds is EqualUnmodifiableListView) return _ensayoIds;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_ensayoIds);
}

 final  List<EnsayoReserva> _ensayos;
@override@JsonKey() List<EnsayoReserva> get ensayos {
  if (_ensayos is EqualUnmodifiableListView) return _ensayos;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_ensayos);
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
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _Reserva&&(identical(other.id, id) || other.id == id)&&(identical(other.usuarioId, usuarioId) || other.usuarioId == usuarioId)&&(identical(other.espacioId, espacioId) || other.espacioId == espacioId)&&(identical(other.fecha, fecha) || other.fecha == fecha)&&(identical(other.horaInicio, horaInicio) || other.horaInicio == horaInicio)&&(identical(other.horaFin, horaFin) || other.horaFin == horaFin)&&(identical(other.estado, estado) || other.estado == estado)&&(identical(other.asistentes, asistentes) || other.asistentes == asistentes)&&(identical(other.tipo, tipo) || other.tipo == tipo)&&(identical(other.asistio, asistio) || other.asistio == asistio)&&(identical(other.motivoRechazo, motivoRechazo) || other.motivoRechazo == motivoRechazo)&&(identical(other.descripcion, descripcion) || other.descripcion == descripcion)&&(identical(other.tipoSolicitud, tipoSolicitud) || other.tipoSolicitud == tipoSolicitud)&&(identical(other.ubicacionUso, ubicacionUso) || other.ubicacionUso == ubicacionUso)&&(identical(other.requiereApoyoAuxiliar, requiereApoyoAuxiliar) || other.requiereApoyoAuxiliar == requiereApoyoAuxiliar)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.updatedAt, updatedAt) || other.updatedAt == updatedAt)&&(identical(other.usuario, usuario) || other.usuario == usuario)&&(identical(other.espacio, espacio) || other.espacio == espacio)&&(identical(other.serieId, serieId) || other.serieId == serieId)&&const DeepCollectionEquality().equals(other._recursoIds, _recursoIds)&&const DeepCollectionEquality().equals(other._recursos, _recursos)&&const DeepCollectionEquality().equals(other._zonaIds, _zonaIds)&&const DeepCollectionEquality().equals(other._zonas, _zonas)&&const DeepCollectionEquality().equals(other._ensayoIds, _ensayoIds)&&const DeepCollectionEquality().equals(other._ensayos, _ensayos)&&const DeepCollectionEquality().equals(other._acompanantes, _acompanantes));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hashAll([runtimeType,id,usuarioId,espacioId,fecha,horaInicio,horaFin,estado,asistentes,tipo,asistio,motivoRechazo,descripcion,tipoSolicitud,ubicacionUso,requiereApoyoAuxiliar,createdAt,updatedAt,usuario,espacio,serieId,const DeepCollectionEquality().hash(_recursoIds),const DeepCollectionEquality().hash(_recursos),const DeepCollectionEquality().hash(_zonaIds),const DeepCollectionEquality().hash(_zonas),const DeepCollectionEquality().hash(_ensayoIds),const DeepCollectionEquality().hash(_ensayos),const DeepCollectionEquality().hash(_acompanantes)]);

@override
String toString() {
  return 'Reserva(id: $id, usuarioId: $usuarioId, espacioId: $espacioId, fecha: $fecha, horaInicio: $horaInicio, horaFin: $horaFin, estado: $estado, asistentes: $asistentes, tipo: $tipo, asistio: $asistio, motivoRechazo: $motivoRechazo, descripcion: $descripcion, tipoSolicitud: $tipoSolicitud, ubicacionUso: $ubicacionUso, requiereApoyoAuxiliar: $requiereApoyoAuxiliar, createdAt: $createdAt, updatedAt: $updatedAt, usuario: $usuario, espacio: $espacio, serieId: $serieId, recursoIds: $recursoIds, recursos: $recursos, zonaIds: $zonaIds, zonas: $zonas, ensayoIds: $ensayoIds, ensayos: $ensayos, acompanantes: $acompanantes)';
}


}

/// @nodoc
abstract mixin class _$ReservaCopyWith<$Res> implements $ReservaCopyWith<$Res> {
  factory _$ReservaCopyWith(_Reserva value, $Res Function(_Reserva) _then) = __$ReservaCopyWithImpl;
@override @useResult
$Res call({
 int id, int usuarioId, int espacioId, String fecha, String horaInicio, String horaFin, EstadoReserva estado, int asistentes, TipoReserva? tipo, bool? asistio, String? motivoRechazo, String? descripcion, TipoSolicitud tipoSolicitud, String? ubicacionUso, bool requiereApoyoAuxiliar, String createdAt, String updatedAt, UsuarioReserva usuario, EspacioReserva espacio, String? serieId, List<int> recursoIds, List<RecursoReserva> recursos, List<int> zonaIds, List<ZonaReserva> zonas, List<int> ensayoIds, List<EnsayoReserva> ensayos, List<ReservaAcompanante> acompanantes
});


@override $UsuarioReservaCopyWith<$Res> get usuario;@override $EspacioReservaCopyWith<$Res> get espacio;

}
/// @nodoc
class __$ReservaCopyWithImpl<$Res>
    implements _$ReservaCopyWith<$Res> {
  __$ReservaCopyWithImpl(this._self, this._then);

  final _Reserva _self;
  final $Res Function(_Reserva) _then;

/// Create a copy of Reserva
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? usuarioId = null,Object? espacioId = null,Object? fecha = null,Object? horaInicio = null,Object? horaFin = null,Object? estado = null,Object? asistentes = null,Object? tipo = freezed,Object? asistio = freezed,Object? motivoRechazo = freezed,Object? descripcion = freezed,Object? tipoSolicitud = null,Object? ubicacionUso = freezed,Object? requiereApoyoAuxiliar = null,Object? createdAt = null,Object? updatedAt = null,Object? usuario = null,Object? espacio = null,Object? serieId = freezed,Object? recursoIds = null,Object? recursos = null,Object? zonaIds = null,Object? zonas = null,Object? ensayoIds = null,Object? ensayos = null,Object? acompanantes = null,}) {
  return _then(_Reserva(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,usuarioId: null == usuarioId ? _self.usuarioId : usuarioId // ignore: cast_nullable_to_non_nullable
as int,espacioId: null == espacioId ? _self.espacioId : espacioId // ignore: cast_nullable_to_non_nullable
as int,fecha: null == fecha ? _self.fecha : fecha // ignore: cast_nullable_to_non_nullable
as String,horaInicio: null == horaInicio ? _self.horaInicio : horaInicio // ignore: cast_nullable_to_non_nullable
as String,horaFin: null == horaFin ? _self.horaFin : horaFin // ignore: cast_nullable_to_non_nullable
as String,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as EstadoReserva,asistentes: null == asistentes ? _self.asistentes : asistentes // ignore: cast_nullable_to_non_nullable
as int,tipo: freezed == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as TipoReserva?,asistio: freezed == asistio ? _self.asistio : asistio // ignore: cast_nullable_to_non_nullable
as bool?,motivoRechazo: freezed == motivoRechazo ? _self.motivoRechazo : motivoRechazo // ignore: cast_nullable_to_non_nullable
as String?,descripcion: freezed == descripcion ? _self.descripcion : descripcion // ignore: cast_nullable_to_non_nullable
as String?,tipoSolicitud: null == tipoSolicitud ? _self.tipoSolicitud : tipoSolicitud // ignore: cast_nullable_to_non_nullable
as TipoSolicitud,ubicacionUso: freezed == ubicacionUso ? _self.ubicacionUso : ubicacionUso // ignore: cast_nullable_to_non_nullable
as String?,requiereApoyoAuxiliar: null == requiereApoyoAuxiliar ? _self.requiereApoyoAuxiliar : requiereApoyoAuxiliar // ignore: cast_nullable_to_non_nullable
as bool,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as String,usuario: null == usuario ? _self.usuario : usuario // ignore: cast_nullable_to_non_nullable
as UsuarioReserva,espacio: null == espacio ? _self.espacio : espacio // ignore: cast_nullable_to_non_nullable
as EspacioReserva,serieId: freezed == serieId ? _self.serieId : serieId // ignore: cast_nullable_to_non_nullable
as String?,recursoIds: null == recursoIds ? _self._recursoIds : recursoIds // ignore: cast_nullable_to_non_nullable
as List<int>,recursos: null == recursos ? _self._recursos : recursos // ignore: cast_nullable_to_non_nullable
as List<RecursoReserva>,zonaIds: null == zonaIds ? _self._zonaIds : zonaIds // ignore: cast_nullable_to_non_nullable
as List<int>,zonas: null == zonas ? _self._zonas : zonas // ignore: cast_nullable_to_non_nullable
as List<ZonaReserva>,ensayoIds: null == ensayoIds ? _self._ensayoIds : ensayoIds // ignore: cast_nullable_to_non_nullable
as List<int>,ensayos: null == ensayos ? _self._ensayos : ensayos // ignore: cast_nullable_to_non_nullable
as List<EnsayoReserva>,acompanantes: null == acompanantes ? _self._acompanantes : acompanantes // ignore: cast_nullable_to_non_nullable
as List<ReservaAcompanante>,
  ));
}

/// Create a copy of Reserva
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
$EspacioReservaCopyWith<$Res> get espacio {
  
  return $EspacioReservaCopyWith<$Res>(_self.espacio, (value) {
    return _then(_self.copyWith(espacio: value));
  });
}
}


/// @nodoc
mixin _$OcurrenciaOmitida {

 String get fecha; String get motivo;
/// Create a copy of OcurrenciaOmitida
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$OcurrenciaOmitidaCopyWith<OcurrenciaOmitida> get copyWith => _$OcurrenciaOmitidaCopyWithImpl<OcurrenciaOmitida>(this as OcurrenciaOmitida, _$identity);

  /// Serializes this OcurrenciaOmitida to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is OcurrenciaOmitida&&(identical(other.fecha, fecha) || other.fecha == fecha)&&(identical(other.motivo, motivo) || other.motivo == motivo));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,fecha,motivo);

@override
String toString() {
  return 'OcurrenciaOmitida(fecha: $fecha, motivo: $motivo)';
}


}

/// @nodoc
abstract mixin class $OcurrenciaOmitidaCopyWith<$Res>  {
  factory $OcurrenciaOmitidaCopyWith(OcurrenciaOmitida value, $Res Function(OcurrenciaOmitida) _then) = _$OcurrenciaOmitidaCopyWithImpl;
@useResult
$Res call({
 String fecha, String motivo
});




}
/// @nodoc
class _$OcurrenciaOmitidaCopyWithImpl<$Res>
    implements $OcurrenciaOmitidaCopyWith<$Res> {
  _$OcurrenciaOmitidaCopyWithImpl(this._self, this._then);

  final OcurrenciaOmitida _self;
  final $Res Function(OcurrenciaOmitida) _then;

/// Create a copy of OcurrenciaOmitida
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? fecha = null,Object? motivo = null,}) {
  return _then(OcurrenciaOmitida(
fecha: null == fecha ? _self.fecha : fecha // ignore: cast_nullable_to_non_nullable
as String,motivo: null == motivo ? _self.motivo : motivo // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [OcurrenciaOmitida].
extension OcurrenciaOmitidaPatterns on OcurrenciaOmitida {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _OcurrenciaOmitida value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _OcurrenciaOmitida() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _OcurrenciaOmitida value)  $default,){
final _that = this;
switch (_that) {
case _OcurrenciaOmitida():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _OcurrenciaOmitida value)?  $default,){
final _that = this;
switch (_that) {
case _OcurrenciaOmitida() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String fecha,  String motivo)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _OcurrenciaOmitida() when $default != null:
return $default(_that.fecha,_that.motivo);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String fecha,  String motivo)  $default,) {final _that = this;
switch (_that) {
case _OcurrenciaOmitida():
return $default(_that.fecha,_that.motivo);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String fecha,  String motivo)?  $default,) {final _that = this;
switch (_that) {
case _OcurrenciaOmitida() when $default != null:
return $default(_that.fecha,_that.motivo);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _OcurrenciaOmitida implements OcurrenciaOmitida {
  const _OcurrenciaOmitida({required this.fecha, required this.motivo});
  factory _OcurrenciaOmitida.fromJson(Map<String, dynamic> json) => _$OcurrenciaOmitidaFromJson(json);

@override final  String fecha;
@override final  String motivo;

/// Create a copy of OcurrenciaOmitida
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$OcurrenciaOmitidaCopyWith<_OcurrenciaOmitida> get copyWith => __$OcurrenciaOmitidaCopyWithImpl<_OcurrenciaOmitida>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$OcurrenciaOmitidaToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _OcurrenciaOmitida&&(identical(other.fecha, fecha) || other.fecha == fecha)&&(identical(other.motivo, motivo) || other.motivo == motivo));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,fecha,motivo);

@override
String toString() {
  return 'OcurrenciaOmitida(fecha: $fecha, motivo: $motivo)';
}


}

/// @nodoc
abstract mixin class _$OcurrenciaOmitidaCopyWith<$Res> implements $OcurrenciaOmitidaCopyWith<$Res> {
  factory _$OcurrenciaOmitidaCopyWith(_OcurrenciaOmitida value, $Res Function(_OcurrenciaOmitida) _then) = __$OcurrenciaOmitidaCopyWithImpl;
@override @useResult
$Res call({
 String fecha, String motivo
});




}
/// @nodoc
class __$OcurrenciaOmitidaCopyWithImpl<$Res>
    implements _$OcurrenciaOmitidaCopyWith<$Res> {
  __$OcurrenciaOmitidaCopyWithImpl(this._self, this._then);

  final _OcurrenciaOmitida _self;
  final $Res Function(_OcurrenciaOmitida) _then;

/// Create a copy of OcurrenciaOmitida
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? fecha = null,Object? motivo = null,}) {
  return _then(_OcurrenciaOmitida(
fecha: null == fecha ? _self.fecha : fecha // ignore: cast_nullable_to_non_nullable
as String,motivo: null == motivo ? _self.motivo : motivo // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$ReservaSerieResultado {

 List<Reserva> get creadas; List<OcurrenciaOmitida> get omitidas;
/// Create a copy of ReservaSerieResultado
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ReservaSerieResultadoCopyWith<ReservaSerieResultado> get copyWith => _$ReservaSerieResultadoCopyWithImpl<ReservaSerieResultado>(this as ReservaSerieResultado, _$identity);

  /// Serializes this ReservaSerieResultado to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ReservaSerieResultado&&const DeepCollectionEquality().equals(other.creadas, creadas)&&const DeepCollectionEquality().equals(other.omitidas, omitidas));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(creadas),const DeepCollectionEquality().hash(omitidas));

@override
String toString() {
  return 'ReservaSerieResultado(creadas: $creadas, omitidas: $omitidas)';
}


}

/// @nodoc
abstract mixin class $ReservaSerieResultadoCopyWith<$Res>  {
  factory $ReservaSerieResultadoCopyWith(ReservaSerieResultado value, $Res Function(ReservaSerieResultado) _then) = _$ReservaSerieResultadoCopyWithImpl;
@useResult
$Res call({
 List<Reserva> creadas, List<OcurrenciaOmitida> omitidas
});




}
/// @nodoc
class _$ReservaSerieResultadoCopyWithImpl<$Res>
    implements $ReservaSerieResultadoCopyWith<$Res> {
  _$ReservaSerieResultadoCopyWithImpl(this._self, this._then);

  final ReservaSerieResultado _self;
  final $Res Function(ReservaSerieResultado) _then;

/// Create a copy of ReservaSerieResultado
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? creadas = null,Object? omitidas = null,}) {
  return _then(ReservaSerieResultado(
creadas: null == creadas ? _self.creadas : creadas // ignore: cast_nullable_to_non_nullable
as List<Reserva>,omitidas: null == omitidas ? _self.omitidas : omitidas // ignore: cast_nullable_to_non_nullable
as List<OcurrenciaOmitida>,
  ));
}

}


/// Adds pattern-matching-related methods to [ReservaSerieResultado].
extension ReservaSerieResultadoPatterns on ReservaSerieResultado {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ReservaSerieResultado value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ReservaSerieResultado() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ReservaSerieResultado value)  $default,){
final _that = this;
switch (_that) {
case _ReservaSerieResultado():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ReservaSerieResultado value)?  $default,){
final _that = this;
switch (_that) {
case _ReservaSerieResultado() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( List<Reserva> creadas,  List<OcurrenciaOmitida> omitidas)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ReservaSerieResultado() when $default != null:
return $default(_that.creadas,_that.omitidas);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( List<Reserva> creadas,  List<OcurrenciaOmitida> omitidas)  $default,) {final _that = this;
switch (_that) {
case _ReservaSerieResultado():
return $default(_that.creadas,_that.omitidas);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( List<Reserva> creadas,  List<OcurrenciaOmitida> omitidas)?  $default,) {final _that = this;
switch (_that) {
case _ReservaSerieResultado() when $default != null:
return $default(_that.creadas,_that.omitidas);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ReservaSerieResultado implements ReservaSerieResultado {
  const _ReservaSerieResultado({required  List<Reserva> creadas, required  List<OcurrenciaOmitida> omitidas}): _creadas = creadas,_omitidas = omitidas;
  factory _ReservaSerieResultado.fromJson(Map<String, dynamic> json) => _$ReservaSerieResultadoFromJson(json);

 final  List<Reserva> _creadas;
@override List<Reserva> get creadas {
  if (_creadas is EqualUnmodifiableListView) return _creadas;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_creadas);
}

 final  List<OcurrenciaOmitida> _omitidas;
@override List<OcurrenciaOmitida> get omitidas {
  if (_omitidas is EqualUnmodifiableListView) return _omitidas;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_omitidas);
}


/// Create a copy of ReservaSerieResultado
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ReservaSerieResultadoCopyWith<_ReservaSerieResultado> get copyWith => __$ReservaSerieResultadoCopyWithImpl<_ReservaSerieResultado>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ReservaSerieResultadoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ReservaSerieResultado&&const DeepCollectionEquality().equals(other._creadas, _creadas)&&const DeepCollectionEquality().equals(other._omitidas, _omitidas));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_creadas),const DeepCollectionEquality().hash(_omitidas));

@override
String toString() {
  return 'ReservaSerieResultado(creadas: $creadas, omitidas: $omitidas)';
}


}

/// @nodoc
abstract mixin class _$ReservaSerieResultadoCopyWith<$Res> implements $ReservaSerieResultadoCopyWith<$Res> {
  factory _$ReservaSerieResultadoCopyWith(_ReservaSerieResultado value, $Res Function(_ReservaSerieResultado) _then) = __$ReservaSerieResultadoCopyWithImpl;
@override @useResult
$Res call({
 List<Reserva> creadas, List<OcurrenciaOmitida> omitidas
});




}
/// @nodoc
class __$ReservaSerieResultadoCopyWithImpl<$Res>
    implements _$ReservaSerieResultadoCopyWith<$Res> {
  __$ReservaSerieResultadoCopyWithImpl(this._self, this._then);

  final _ReservaSerieResultado _self;
  final $Res Function(_ReservaSerieResultado) _then;

/// Create a copy of ReservaSerieResultado
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? creadas = null,Object? omitidas = null,}) {
  return _then(_ReservaSerieResultado(
creadas: null == creadas ? _self._creadas : creadas // ignore: cast_nullable_to_non_nullable
as List<Reserva>,omitidas: null == omitidas ? _self._omitidas : omitidas // ignore: cast_nullable_to_non_nullable
as List<OcurrenciaOmitida>,
  ));
}


}


/// @nodoc
mixin _$OcurrenciaCancelOmitida {

 int get reservaId; String get motivo;
/// Create a copy of OcurrenciaCancelOmitida
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$OcurrenciaCancelOmitidaCopyWith<OcurrenciaCancelOmitida> get copyWith => _$OcurrenciaCancelOmitidaCopyWithImpl<OcurrenciaCancelOmitida>(this as OcurrenciaCancelOmitida, _$identity);

  /// Serializes this OcurrenciaCancelOmitida to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is OcurrenciaCancelOmitida&&(identical(other.reservaId, reservaId) || other.reservaId == reservaId)&&(identical(other.motivo, motivo) || other.motivo == motivo));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,reservaId,motivo);

@override
String toString() {
  return 'OcurrenciaCancelOmitida(reservaId: $reservaId, motivo: $motivo)';
}


}

/// @nodoc
abstract mixin class $OcurrenciaCancelOmitidaCopyWith<$Res>  {
  factory $OcurrenciaCancelOmitidaCopyWith(OcurrenciaCancelOmitida value, $Res Function(OcurrenciaCancelOmitida) _then) = _$OcurrenciaCancelOmitidaCopyWithImpl;
@useResult
$Res call({
 int reservaId, String motivo
});




}
/// @nodoc
class _$OcurrenciaCancelOmitidaCopyWithImpl<$Res>
    implements $OcurrenciaCancelOmitidaCopyWith<$Res> {
  _$OcurrenciaCancelOmitidaCopyWithImpl(this._self, this._then);

  final OcurrenciaCancelOmitida _self;
  final $Res Function(OcurrenciaCancelOmitida) _then;

/// Create a copy of OcurrenciaCancelOmitida
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? reservaId = null,Object? motivo = null,}) {
  return _then(OcurrenciaCancelOmitida(
reservaId: null == reservaId ? _self.reservaId : reservaId // ignore: cast_nullable_to_non_nullable
as int,motivo: null == motivo ? _self.motivo : motivo // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [OcurrenciaCancelOmitida].
extension OcurrenciaCancelOmitidaPatterns on OcurrenciaCancelOmitida {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _OcurrenciaCancelOmitida value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _OcurrenciaCancelOmitida() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _OcurrenciaCancelOmitida value)  $default,){
final _that = this;
switch (_that) {
case _OcurrenciaCancelOmitida():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _OcurrenciaCancelOmitida value)?  $default,){
final _that = this;
switch (_that) {
case _OcurrenciaCancelOmitida() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int reservaId,  String motivo)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _OcurrenciaCancelOmitida() when $default != null:
return $default(_that.reservaId,_that.motivo);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int reservaId,  String motivo)  $default,) {final _that = this;
switch (_that) {
case _OcurrenciaCancelOmitida():
return $default(_that.reservaId,_that.motivo);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int reservaId,  String motivo)?  $default,) {final _that = this;
switch (_that) {
case _OcurrenciaCancelOmitida() when $default != null:
return $default(_that.reservaId,_that.motivo);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _OcurrenciaCancelOmitida implements OcurrenciaCancelOmitida {
  const _OcurrenciaCancelOmitida({required this.reservaId, required this.motivo});
  factory _OcurrenciaCancelOmitida.fromJson(Map<String, dynamic> json) => _$OcurrenciaCancelOmitidaFromJson(json);

@override final  int reservaId;
@override final  String motivo;

/// Create a copy of OcurrenciaCancelOmitida
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$OcurrenciaCancelOmitidaCopyWith<_OcurrenciaCancelOmitida> get copyWith => __$OcurrenciaCancelOmitidaCopyWithImpl<_OcurrenciaCancelOmitida>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$OcurrenciaCancelOmitidaToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _OcurrenciaCancelOmitida&&(identical(other.reservaId, reservaId) || other.reservaId == reservaId)&&(identical(other.motivo, motivo) || other.motivo == motivo));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,reservaId,motivo);

@override
String toString() {
  return 'OcurrenciaCancelOmitida(reservaId: $reservaId, motivo: $motivo)';
}


}

/// @nodoc
abstract mixin class _$OcurrenciaCancelOmitidaCopyWith<$Res> implements $OcurrenciaCancelOmitidaCopyWith<$Res> {
  factory _$OcurrenciaCancelOmitidaCopyWith(_OcurrenciaCancelOmitida value, $Res Function(_OcurrenciaCancelOmitida) _then) = __$OcurrenciaCancelOmitidaCopyWithImpl;
@override @useResult
$Res call({
 int reservaId, String motivo
});




}
/// @nodoc
class __$OcurrenciaCancelOmitidaCopyWithImpl<$Res>
    implements _$OcurrenciaCancelOmitidaCopyWith<$Res> {
  __$OcurrenciaCancelOmitidaCopyWithImpl(this._self, this._then);

  final _OcurrenciaCancelOmitida _self;
  final $Res Function(_OcurrenciaCancelOmitida) _then;

/// Create a copy of OcurrenciaCancelOmitida
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? reservaId = null,Object? motivo = null,}) {
  return _then(_OcurrenciaCancelOmitida(
reservaId: null == reservaId ? _self.reservaId : reservaId // ignore: cast_nullable_to_non_nullable
as int,motivo: null == motivo ? _self.motivo : motivo // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$ReservaSerieCancelResultado {

 List<Reserva> get canceladas; List<OcurrenciaCancelOmitida> get omitidas;
/// Create a copy of ReservaSerieCancelResultado
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ReservaSerieCancelResultadoCopyWith<ReservaSerieCancelResultado> get copyWith => _$ReservaSerieCancelResultadoCopyWithImpl<ReservaSerieCancelResultado>(this as ReservaSerieCancelResultado, _$identity);

  /// Serializes this ReservaSerieCancelResultado to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ReservaSerieCancelResultado&&const DeepCollectionEquality().equals(other.canceladas, canceladas)&&const DeepCollectionEquality().equals(other.omitidas, omitidas));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(canceladas),const DeepCollectionEquality().hash(omitidas));

@override
String toString() {
  return 'ReservaSerieCancelResultado(canceladas: $canceladas, omitidas: $omitidas)';
}


}

/// @nodoc
abstract mixin class $ReservaSerieCancelResultadoCopyWith<$Res>  {
  factory $ReservaSerieCancelResultadoCopyWith(ReservaSerieCancelResultado value, $Res Function(ReservaSerieCancelResultado) _then) = _$ReservaSerieCancelResultadoCopyWithImpl;
@useResult
$Res call({
 List<Reserva> canceladas, List<OcurrenciaCancelOmitida> omitidas
});




}
/// @nodoc
class _$ReservaSerieCancelResultadoCopyWithImpl<$Res>
    implements $ReservaSerieCancelResultadoCopyWith<$Res> {
  _$ReservaSerieCancelResultadoCopyWithImpl(this._self, this._then);

  final ReservaSerieCancelResultado _self;
  final $Res Function(ReservaSerieCancelResultado) _then;

/// Create a copy of ReservaSerieCancelResultado
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? canceladas = null,Object? omitidas = null,}) {
  return _then(ReservaSerieCancelResultado(
canceladas: null == canceladas ? _self.canceladas : canceladas // ignore: cast_nullable_to_non_nullable
as List<Reserva>,omitidas: null == omitidas ? _self.omitidas : omitidas // ignore: cast_nullable_to_non_nullable
as List<OcurrenciaCancelOmitida>,
  ));
}

}


/// Adds pattern-matching-related methods to [ReservaSerieCancelResultado].
extension ReservaSerieCancelResultadoPatterns on ReservaSerieCancelResultado {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ReservaSerieCancelResultado value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ReservaSerieCancelResultado() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ReservaSerieCancelResultado value)  $default,){
final _that = this;
switch (_that) {
case _ReservaSerieCancelResultado():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ReservaSerieCancelResultado value)?  $default,){
final _that = this;
switch (_that) {
case _ReservaSerieCancelResultado() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( List<Reserva> canceladas,  List<OcurrenciaCancelOmitida> omitidas)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ReservaSerieCancelResultado() when $default != null:
return $default(_that.canceladas,_that.omitidas);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( List<Reserva> canceladas,  List<OcurrenciaCancelOmitida> omitidas)  $default,) {final _that = this;
switch (_that) {
case _ReservaSerieCancelResultado():
return $default(_that.canceladas,_that.omitidas);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( List<Reserva> canceladas,  List<OcurrenciaCancelOmitida> omitidas)?  $default,) {final _that = this;
switch (_that) {
case _ReservaSerieCancelResultado() when $default != null:
return $default(_that.canceladas,_that.omitidas);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ReservaSerieCancelResultado implements ReservaSerieCancelResultado {
  const _ReservaSerieCancelResultado({required  List<Reserva> canceladas, required  List<OcurrenciaCancelOmitida> omitidas}): _canceladas = canceladas,_omitidas = omitidas;
  factory _ReservaSerieCancelResultado.fromJson(Map<String, dynamic> json) => _$ReservaSerieCancelResultadoFromJson(json);

 final  List<Reserva> _canceladas;
@override List<Reserva> get canceladas {
  if (_canceladas is EqualUnmodifiableListView) return _canceladas;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_canceladas);
}

 final  List<OcurrenciaCancelOmitida> _omitidas;
@override List<OcurrenciaCancelOmitida> get omitidas {
  if (_omitidas is EqualUnmodifiableListView) return _omitidas;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_omitidas);
}


/// Create a copy of ReservaSerieCancelResultado
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ReservaSerieCancelResultadoCopyWith<_ReservaSerieCancelResultado> get copyWith => __$ReservaSerieCancelResultadoCopyWithImpl<_ReservaSerieCancelResultado>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ReservaSerieCancelResultadoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ReservaSerieCancelResultado&&const DeepCollectionEquality().equals(other._canceladas, _canceladas)&&const DeepCollectionEquality().equals(other._omitidas, _omitidas));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_canceladas),const DeepCollectionEquality().hash(_omitidas));

@override
String toString() {
  return 'ReservaSerieCancelResultado(canceladas: $canceladas, omitidas: $omitidas)';
}


}

/// @nodoc
abstract mixin class _$ReservaSerieCancelResultadoCopyWith<$Res> implements $ReservaSerieCancelResultadoCopyWith<$Res> {
  factory _$ReservaSerieCancelResultadoCopyWith(_ReservaSerieCancelResultado value, $Res Function(_ReservaSerieCancelResultado) _then) = __$ReservaSerieCancelResultadoCopyWithImpl;
@override @useResult
$Res call({
 List<Reserva> canceladas, List<OcurrenciaCancelOmitida> omitidas
});




}
/// @nodoc
class __$ReservaSerieCancelResultadoCopyWithImpl<$Res>
    implements _$ReservaSerieCancelResultadoCopyWith<$Res> {
  __$ReservaSerieCancelResultadoCopyWithImpl(this._self, this._then);

  final _ReservaSerieCancelResultado _self;
  final $Res Function(_ReservaSerieCancelResultado) _then;

/// Create a copy of ReservaSerieCancelResultado
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? canceladas = null,Object? omitidas = null,}) {
  return _then(_ReservaSerieCancelResultado(
canceladas: null == canceladas ? _self._canceladas : canceladas // ignore: cast_nullable_to_non_nullable
as List<Reserva>,omitidas: null == omitidas ? _self._omitidas : omitidas // ignore: cast_nullable_to_non_nullable
as List<OcurrenciaCancelOmitida>,
  ));
}


}

// dart format on
