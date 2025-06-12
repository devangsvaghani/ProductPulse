import React, { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";
import toast from "react-hot-toast";

const Spinner = () => (
    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
);

const UserFormModal = ({ user, onClose, onSave }) => {
    const [formData, setFormData] = useState({
        email: "",
        nickname: "",
        password: "",
        is_admin: false,
    });
    const [isSaving, setIsSaving] = useState(false);

    useEffect(() => {
        if (user) {
            setFormData({
                email: user.email || "",
                nickname: user.nickname || "",
                password: "",
                is_admin: user.is_admin || false,
            });
        } else {
            setFormData({
                email: "",
                nickname: "",
                password: "",
                is_admin: false,
            });
        }
    }, [user]);

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: type === "checkbox" ? checked : value,
        }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        setIsSaving(true);
        onSave(formData);
        setIsSaving(false);
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-20">
            <div className="bg-white p-8 rounded-lg shadow-xl w-full max-w-md">
                <h2 className="text-2xl font-bold mb-4">
                    {user ? "Edit User" : "Create New User"}
                </h2>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700">
                            Email
                        </label>
                        <input
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            required
                            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">
                            Nickname
                        </label>
                        <input
                            type="text"
                            name="nickname"
                            value={formData.nickname}
                            onChange={handleChange}
                            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                        />
                    </div>
                    {!user && (
                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                Password
                            </label>
                            <input
                                type="password"
                                name="password"
                                value={formData.password}
                                onChange={handleChange}
                                required
                                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                            />
                        </div>
                    )}
                    <div className="flex items-center">
                        <input
                            type="checkbox"
                            name="is_admin"
                            checked={formData.is_admin}
                            onChange={handleChange}
                            className="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                        />
                        <label className="ml-2 block text-sm text-gray-900">
                            Is Admin?
                        </label>
                    </div>
                    <div className="flex justify-end space-x-4 pt-4">
                        <button
                            type="button"
                            onClick={onClose}
                            className="bg-gray-200 text-gray-800 font-bold py-2 px-4 rounded hover:bg-gray-300"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="bg-indigo-600 text-white font-bold py-2 px-4 rounded hover:bg-indigo-700 flex items-center justify-center w-24"
                            disabled={isSaving} 
                        >
                            {isSaving ? <Spinner /> : "Save"}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

const UserManagementPage = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [editingUser, setEditingUser] = useState(null);
    const [isCreateModalOpen, setCreateModalOpen] = useState(false);

    const fetchUsers = useCallback(async () => {
        try {
            setLoading(true);
            const response = await api.get("/api/v1/admin/users");
            setUsers(response.data);
        } catch (error) {
            console.error("Failed to fetch users", error);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchUsers();
    }, [fetchUsers]);

    const handleSaveUser = async (userData) => {
        const action = editingUser ? "Updating" : "Creating";
        const promise = editingUser
            ? api.put(`/api/v1/admin/users/${editingUser.id}`, {
                  email: userData.email,
                  nickname: userData.nickname,
                  is_admin: userData.is_admin,
              })
            : api.post("/api/v1/admin/users", userData);

        try {
            await toast.promise(promise, {
                loading: `${action} user...`,
                success: `User ${
                    action === "Updating" ? "updated" : "created"
                } successfully!`,
                error: `Failed to ${action.toLowerCase()} user.`,
            });
            fetchUsers();
            closeModal();
        } catch (error) {
            console.error(error);
        }
    };

    const handleDeleteUser = async (userId) => {
        if (
            window.confirm(
                "Are you sure you want to delete this user? This action cannot be undone."
            )
        ) {
            try {
                await toast.promise(
                    api.delete(`/api/v1/admin/users/${userId}`),
                    {
                        loading: "Deleting user...",
                        success: "User deleted successfully!",
                        error: "Failed to delete user.",
                    }
                );
                fetchUsers();
            } catch (error) {
                console.error(error);
            }
        }
    };

    const openCreateModal = () => {
        setEditingUser(null);
        setCreateModalOpen(true);
    };

    const openEditModal = (user) => {
        setCreateModalOpen(false);
        setEditingUser(user);
    };

    const closeModal = () => {
        setEditingUser(null);
        setCreateModalOpen(false);
    };

    const SkeletonRow = () => (
        <li className="px-4 py-4 sm:px-6">
            <div className="h-4 bg-gray-200 rounded w-1/4 animate-pulse"></div>
            <div className="h-3 bg-gray-200 rounded w-1/3 mt-2 animate-pulse"></div>
        </li>
    );

    return (
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <div className="px-4 py-6 sm:px-0">
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h1 className="text-2xl font-semibold text-gray-900">
                            User Management
                        </h1>
                        <Link
                            to="/admin"
                            className="text-sm text-indigo-600 hover:text-indigo-900"
                        >
                            &larr; Back to Admin Dashboard
                        </Link>
                    </div>
                    <button
                        onClick={openCreateModal}
                        className="bg-indigo-600 text-white font-bold py-2 px-4 rounded hover:bg-indigo-700"
                    >
                        Create User
                    </button>
                </div>

                <div className="bg-white shadow overflow-hidden sm:rounded-md">
                    <ul role="list" className="divide-y divide-gray-200">
                        {loading ? (
                            <>
                                <SkeletonRow />
                                <SkeletonRow />
                                <SkeletonRow />
                            </>
                        ) : (
                            users.map((user) => (
                                <li
                                    key={user.email}
                                    className="px-4 py-4 sm:px-6 flex items-center justify-between"
                                >
                                    <div className="flex items-center">
                                        <div className="ml-3">
                                            <p className="text-sm font-medium text-gray-900">
                                                {user.nickname || "No Nickname"}
                                            </p>
                                            <p className="text-sm text-gray-500">
                                                {user.email}
                                            </p>
                                        </div>
                                        {user.is_admin && (
                                            <span className="ml-4 px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                                                Admin
                                            </span>
                                        )}
                                    </div>
                                    <div className="space-x-4">
                                        <button
                                            onClick={() => openEditModal(user)}
                                            className="text-indigo-600 hover:text-indigo-900 font-medium"
                                        >
                                            Edit
                                        </button>
                                        <button
                                            onClick={() =>
                                                handleDeleteUser(user.id)
                                            }
                                            className="text-red-600 hover:text-red-900 font-medium"
                                        >
                                            Delete
                                        </button>
                                    </div>
                                </li>
                            ))
                        )}
                    </ul>
                </div>
            </div>
            {(isCreateModalOpen || editingUser) && (
                <UserFormModal
                    user={editingUser}
                    onClose={closeModal}
                    onSave={handleSaveUser}
                />
            )}
        </div>
    );
};

export default UserManagementPage;
