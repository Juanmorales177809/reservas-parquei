// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'control_cambio.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ControlCambio {

 int get id; int? get usuarioId; String get usuario; String get accion; String get entidad; int? get entidadId; String get descripcion; String get createdAt;
/// Create a copy of ControlCambio
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ControlCambioCopyWith<ControlCambio> get copyWith => _$ControlCambioCopyWithImpl<ControlCambio>(this as ControlCambio, _$identity);

  /// Serializes this ControlCambio to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ControlCambio&&(identical(other.id, id) || other.id == id)&&(identical(other.usuarioId, usuarioId) || other.usuarioId == usuarioId)&&(identical(other.usuario, usuario) || other.usuario == usuario)&&(identical(other.accion, accion) || other.accion == accion)&&(identical(other.entidad, entidad) || other.entidad == entidad)&&(identical(other.entidadId, entidadId) || other.entidadId == entidadId)&&(identical(other.descripcion, descripcion) || other.descripcion == descripcion)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,usuarioId,usuario,accion,entidad,entidadId,descripcion,createdAt);

@override
String toString() {
  return 'ControlCambio(id: $id, usuarioId: $usuarioId, usuario: $usuario, accion: $accion, entidad: $entidad, entidadId: $entidadId, descripcion: $descripcion, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class $ControlCambioCopyWith<$Res>  {
  factory $ControlCambioCopyWith(ControlCambio value, $Res Function(ControlCambio) _then) = _$ControlCambioCopyWithImpl;
@useResult
$Res call({
 int id, int? usuarioId, String usuario, String accion, String entidad, int? entidadId, String descripcion, String createdAt
});




}
/// @nodoc
class _$ControlCambioCopyWithImpl<$Res>
    implements $ControlCambioCopyWith<$Res> {
  _$ControlCambioCopyWithImpl(this._self, this._then);

  final ControlCambio _self;
  final $Res Function(ControlCambio) _then;

/// Create a copy of ControlCambio
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? usuarioId = freezed,Object? usuario = null,Object? accion = null,Object? entidad = null,Object? entidadId = freezed,Object? descripcion = null,Object? createdAt = null,}) {
  return _then(ControlCambio(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,usuarioId: freezed == usuarioId ? _self.usuarioId : usuarioId // ignore: cast_nullable_to_non_nullable
as int?,usuario: null == usuario ? _self.usuario : usuario // ignore: cast_nullable_to_non_nullable
as String,accion: null == accion ? _self.accion : accion // ignore: cast_nullable_to_non_nullable
as String,entidad: null == entidad ? _self.entidad : entidad // ignore: cast_nullable_to_non_nullable
as String,entidadId: freezed == entidadId ? _self.entidadId : entidadId // ignore: cast_nullable_to_non_nullable
as int?,descripcion: null == descripcion ? _self.descripcion : descripcion // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [ControlCambio].
extension ControlCambioPatterns on ControlCambio {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ControlCambio value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ControlCambio() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ControlCambio value)  $default,){
final _that = this;
switch (_that) {
case _ControlCambio():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ControlCambio value)?  $default,){
final _that = this;
switch (_that) {
case _ControlCambio() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  int? usuarioId,  String usuario,  String accion,  String entidad,  int? entidadId,  String descripcion,  String createdAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ControlCambio() when $default != null:
return $default(_that.id,_that.usuarioId,_that.usuario,_that.accion,_that.entidad,_that.entidadId,_that.descripcion,_that.createdAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  int? usuarioId,  String usuario,  String accion,  String entidad,  int? entidadId,  String descripcion,  String createdAt)  $default,) {final _that = this;
switch (_that) {
case _ControlCambio():
return $default(_that.id,_that.usuarioId,_that.usuario,_that.accion,_that.entidad,_that.entidadId,_that.descripcion,_that.createdAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  int? usuarioId,  String usuario,  String accion,  String entidad,  int? entidadId,  String descripcion,  String createdAt)?  $default,) {final _that = this;
switch (_that) {
case _ControlCambio() when $default != null:
return $default(_that.id,_that.usuarioId,_that.usuario,_that.accion,_that.entidad,_that.entidadId,_that.descripcion,_that.createdAt);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ControlCambio implements ControlCambio {
  const _ControlCambio({required this.id, this.usuarioId, required this.usuario, required this.accion, required this.entidad, this.entidadId, required this.descripcion, required this.createdAt});
  factory _ControlCambio.fromJson(Map<String, dynamic> json) => _$ControlCambioFromJson(json);

@override final  int id;
@override final  int? usuarioId;
@override final  String usuario;
@override final  String accion;
@override final  String entidad;
@override final  int? entidadId;
@override final  String descripcion;
@override final  String createdAt;

/// Create a copy of ControlCambio
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ControlCambioCopyWith<_ControlCambio> get copyWith => __$ControlCambioCopyWithImpl<_ControlCambio>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ControlCambioToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ControlCambio&&(identical(other.id, id) || other.id == id)&&(identical(other.usuarioId, usuarioId) || other.usuarioId == usuarioId)&&(identical(other.usuario, usuario) || other.usuario == usuario)&&(identical(other.accion, accion) || other.accion == accion)&&(identical(other.entidad, entidad) || other.entidad == entidad)&&(identical(other.entidadId, entidadId) || other.entidadId == entidadId)&&(identical(other.descripcion, descripcion) || other.descripcion == descripcion)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,usuarioId,usuario,accion,entidad,entidadId,descripcion,createdAt);

@override
String toString() {
  return 'ControlCambio(id: $id, usuarioId: $usuarioId, usuario: $usuario, accion: $accion, entidad: $entidad, entidadId: $entidadId, descripcion: $descripcion, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class _$ControlCambioCopyWith<$Res> implements $ControlCambioCopyWith<$Res> {
  factory _$ControlCambioCopyWith(_ControlCambio value, $Res Function(_ControlCambio) _then) = __$ControlCambioCopyWithImpl;
@override @useResult
$Res call({
 int id, int? usuarioId, String usuario, String accion, String entidad, int? entidadId, String descripcion, String createdAt
});




}
/// @nodoc
class __$ControlCambioCopyWithImpl<$Res>
    implements _$ControlCambioCopyWith<$Res> {
  __$ControlCambioCopyWithImpl(this._self, this._then);

  final _ControlCambio _self;
  final $Res Function(_ControlCambio) _then;

/// Create a copy of ControlCambio
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? usuarioId = freezed,Object? usuario = null,Object? accion = null,Object? entidad = null,Object? entidadId = freezed,Object? descripcion = null,Object? createdAt = null,}) {
  return _then(_ControlCambio(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,usuarioId: freezed == usuarioId ? _self.usuarioId : usuarioId // ignore: cast_nullable_to_non_nullable
as int?,usuario: null == usuario ? _self.usuario : usuario // ignore: cast_nullable_to_non_nullable
as String,accion: null == accion ? _self.accion : accion // ignore: cast_nullable_to_non_nullable
as String,entidad: null == entidad ? _self.entidad : entidad // ignore: cast_nullable_to_non_nullable
as String,entidadId: freezed == entidadId ? _self.entidadId : entidadId // ignore: cast_nullable_to_non_nullable
as int?,descripcion: null == descripcion ? _self.descripcion : descripcion // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
